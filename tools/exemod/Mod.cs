// Ukrainian text for message scripts that live inside P5R.exe (battle navigator lines, battle retry, ...).
//
// The exe embeds one BMD per language and picks it with `lea reg, [rip + blob]` by the language index.
// At start-up this DLL
//   1. loads <mod>/exebmd/<sha1>.bmd — translated BMDs named after the SHA-1 of the English blob they replace
//      (built by tools/scripts/build_mod.py from source_en/EXE, see tools/scripts/exe_bmd.py);
//   2. hashes every BMD ("1GSM" header) in the loaded image and keeps the ones it has a translation for;
//   3. copies the translations into memory allocated within 2 GB of the image;
//   4. rewrites the displacement of every RIP-relative `lea` that points at such a blob.
// Nothing is written to disk except <mod>/exebmd_log.txt. The game files stay untouched.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using Reloaded.Mod.Interfaces;
using Reloaded.Mod.Interfaces.Internal;

namespace P5RUkr
{
    public unsafe class Mod : IMod
    {
        static string _log;

        public void StartEx(IModLoaderV1 loader, IModConfigV1 config)
        {
            var dir = Path.GetDirectoryName(typeof(Mod).Assembly.Location) ?? ".";
            _log = Path.Combine(dir, "exebmd_log.txt");
            try { File.WriteAllText(_log, $"=== start {DateTime.Now:yyyy-MM-dd HH:mm:ss}{Environment.NewLine}"); } catch { }
            var tr = new Dictionary<string, byte[]>(StringComparer.OrdinalIgnoreCase);
            var folder = Path.Combine(dir, "exebmd");
            if (Directory.Exists(folder))
                foreach (var f in Directory.GetFiles(folder, "*.bmd"))
                    tr[Path.GetFileNameWithoutExtension(f)] = File.ReadAllBytes(f);
            Log($"{tr.Count} translated BMDs");
            if (tr.Count == 0) return;
            // the code may still be unpacked by the launcher stub: retry for a while if nothing matched
            new Thread(() =>
            {
                for (int i = 0; i < 60; i++)
                {
                    try { if (Patch(tr)) return; }
                    catch (Exception e) { Log("error: " + e); return; }
                    Thread.Sleep(1000);
                }
                Log("gave up: no references patched");
            }) { IsBackground = true }.Start();
        }

        public void Start(IModLoaderV1 loader) { }
        public void Suspend() { }
        public void Resume() { }
        public void Unload() { }
        public bool CanUnload() => false;
        public bool CanSuspend() => false;
        public Action Disposing { get; }

        static void Log(string s)
        {
            try { File.AppendAllText(_log, s + Environment.NewLine, Encoding.UTF8); } catch { }
        }

        static bool Patch(Dictionary<string, byte[]> tr)
        {
            var module = Process.GetCurrentProcess().MainModule;
            long start = (long)module.BaseAddress, end = start + module.ModuleMemorySize;
            var regions = Regions(start, end);

            // 2. English blobs present in the image -> translation
            var blobs = new Dictionary<long, byte[]>();
            foreach (var (rs, re, _) in regions)
            {
                byte* p = (byte*)rs;
                for (long o = 8; o + 4 <= re - rs; o++)
                {
                    if (p[o] != (byte)'1' || p[o + 1] != (byte)'G' || p[o + 2] != (byte)'S' || p[o + 3] != (byte)'M' || p[o - 8] != 7)
                        continue;
                    long b = rs + o - 8;
                    int size = (p[o - 4] << 24) | (p[o - 3] << 16) | (p[o - 2] << 8) | p[o - 1];
                    if (size < 0x20 || b + size > re) continue;
                    var hash = Convert.ToHexString(SHA1.HashData(new ReadOnlySpan<byte>((void*)b, size))).ToLowerInvariant();
                    if (tr.TryGetValue(hash, out var data))
                    {
                        blobs[b] = data;
                        Log($"blob +{b - start:X} size {size:X} sha1 {hash}");
                    }
                }
            }
            if (blobs.Count == 0) return false;

            // 3. translations near the image (rel32 reach)
            long total = 0;
            foreach (var d in blobs.Values) total += (d.Length + 15) & ~15;
            long mem = AllocNear(end, total);
            if (mem == 0) { Log("could not allocate memory near the image"); return true; }
            var target = new Dictionary<long, long>();
            var placed = new Dictionary<byte[], long>();
            long cur = mem;
            foreach (var (b, d) in blobs)
            {
                if (!placed.TryGetValue(d, out var at))
                {
                    at = cur;
                    Marshal.Copy(d, 0, (IntPtr)at, d.Length);
                    placed[d] = at;
                    cur += (d.Length + 15) & ~15;
                }
                target[b] = at;
            }

            // 4. lea r64, [rip + disp32]: REX.W (48/4C) 8D modrm(mod=00, rm=101)
            int patched = 0;
            foreach (var (rs, re, exec) in regions)
            {
                if (!exec) continue;
                byte* p = (byte*)rs;
                for (long o = 0; o + 7 <= re - rs; o++)
                {
                    if ((p[o] != 0x48 && p[o] != 0x4C) || p[o + 1] != 0x8D || (p[o + 2] & 0xC7) != 0x05) continue;
                    long next = rs + o + 7;
                    long dest = next + *(int*)(p + o + 3);
                    if (!target.TryGetValue(dest, out var nw)) continue;
                    long disp = nw - next;
                    if (disp < int.MinValue || disp > int.MaxValue) { Log($"out of range at +{rs + o - start:X}"); continue; }
                    VirtualProtect((IntPtr)(p + o + 3), (UIntPtr)4, 0x40, out var old);
                    *(int*)(p + o + 3) = (int)disp;
                    VirtualProtect((IntPtr)(p + o + 3), (UIntPtr)4, old, out _);
                    Log($"lea +{rs + o - start:X} -> blob +{dest - start:X}");
                    patched++;
                }
            }
            Log($"{blobs.Count} blobs, {placed.Count} translations, {patched} references patched");
            return patched > 0;
        }

        // committed, readable regions of the image: (start, end, executable)
        static List<(long, long, bool)> Regions(long start, long end)
        {
            var list = new List<(long, long, bool)>();
            for (long a = start; a < end;)
            {
                if (VirtualQuery((IntPtr)a, out var m, (UIntPtr)sizeof(MEMORY_BASIC_INFORMATION)) == UIntPtr.Zero) break;
                long rs = (long)m.BaseAddress, re = Math.Min(end, rs + (long)m.RegionSize);
                uint prot = m.Protect & 0xFF;
                bool readable = m.State == 0x1000 && (m.Protect & 0x100) == 0 &&
                                (prot == 0x02 || prot == 0x04 || prot == 0x08 || prot == 0x20 || prot == 0x40 || prot == 0x80);
                bool exec = prot == 0x20 || prot == 0x40 || prot == 0x80;
                if (readable) list.Add((Math.Max(rs, start), re, exec));
                a = re;
            }
            return list;
        }

        static long AllocNear(long end, long size)
        {
            const long step = 0x10000;
            long from = (end + step - 1) & ~(step - 1);
            for (long a = from; a < from + 0x40000000; a += step)
            {
                var r = VirtualAlloc((IntPtr)a, (UIntPtr)size, 0x3000 /*COMMIT|RESERVE*/, 0x04 /*RW*/);
                if (r != IntPtr.Zero) { Log($"allocated {size:X} at +{a - end:X} after image"); return (long)r; }
            }
            return 0;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct MEMORY_BASIC_INFORMATION
        {
            public IntPtr BaseAddress, AllocationBase;
            public uint AllocationProtect;
            public IntPtr RegionSize;
            public uint State, Protect, Type;
        }

        [DllImport("kernel32.dll")] static extern UIntPtr VirtualQuery(IntPtr a, out MEMORY_BASIC_INFORMATION m, UIntPtr len);
        [DllImport("kernel32.dll")] static extern IntPtr VirtualAlloc(IntPtr a, UIntPtr size, uint type, uint protect);
        [DllImport("kernel32.dll")] static extern bool VirtualProtect(IntPtr a, UIntPtr size, uint prot, out uint old);
    }
}
