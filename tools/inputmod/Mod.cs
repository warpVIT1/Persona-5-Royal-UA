// Diagnostic build of the Ukrainian name-input mod for Persona 5 Royal (Reloaded-II).
//
// Stage 1 (this build) only OBSERVES, it changes nothing in the game:
//   * subclasses the game window and logs keyboard messages (WM_KEYDOWN / WM_CHAR / WM_INPUT / IME),
//     so we learn how the name-entry screen receives text and what arrives with the Ukrainian layout;
//   * on F10 scans the game's writable memory for the test names the tester typed
//     ("Zqzq" / "Xjxj") and logs every hit with surrounding bytes (to find the name buffers and their size).
// Log: <mod folder>/input_log.txt
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using Reloaded.Mod.Interfaces;
using Reloaded.Mod.Interfaces.Internal;

namespace P5RUkrInput
{
    public class Mod : IMod
    {
        static string _log;
        static IntPtr _oldProc;
        static WndProc _proc;   // keep the delegate alive
        static int _logged;

        public void StartEx(IModLoaderV1 loader, IModConfigV1 config)
        {
            _log = Path.Combine(Path.GetDirectoryName(typeof(Mod).Assembly.Location) ?? ".", "input_log.txt");
            Log($"=== start {DateTime.Now:yyyy-MM-dd HH:mm:ss}, pid {Environment.ProcessId}, layout {GetKeyboardLayout(0):X}");
            new Thread(HookWhenWindowExists) { IsBackground = true }.Start();
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

        // ---------- window subclassing ----------
        delegate IntPtr WndProc(IntPtr h, uint msg, IntPtr w, IntPtr l);

        static void HookWhenWindowExists()
        {
            var pid = (uint)Environment.ProcessId;
            for (int i = 0; i < 600; i++)
            {
                IntPtr found = IntPtr.Zero;
                EnumWindows((h, _) =>
                {
                    GetWindowThreadProcessId(h, out var p);
                    if (p == pid && IsWindowVisible(h)) { found = h; return false; }
                    return true;
                }, IntPtr.Zero);
                if (found != IntPtr.Zero)
                {
                    _proc = MyProc;
                    _oldProc = SetWindowLongPtrW(found, -4 /*GWLP_WNDPROC*/, Marshal.GetFunctionPointerForDelegate(_proc));
                    var sb = new StringBuilder(256);
                    GetClassNameW(found, sb, 256);
                    Log($"hooked window {found:X} class '{sb}' oldproc {_oldProc:X}");
                    return;
                }
                Thread.Sleep(500);
            }
            Log("game window not found");
        }

        const uint WM_KEYDOWN = 0x100, WM_CHAR = 0x102, WM_SYSKEYDOWN = 0x104, WM_UNICHAR = 0x109,
                   WM_INPUT = 0x00FF, WM_IME_CHAR = 0x286, WM_IME_COMPOSITION = 0x10F, WM_INPUTLANGCHANGE = 0x51;

        static IntPtr MyProc(IntPtr h, uint msg, IntPtr w, IntPtr l)
        {
            if (msg == WM_KEYDOWN && (int)w == 0x79 /*F10*/)
                new Thread(ScanMemory) { IsBackground = true }.Start();
            if (_logged < 5000 && (msg == WM_KEYDOWN || msg == WM_CHAR || msg == WM_SYSKEYDOWN || msg == WM_UNICHAR ||
                                   msg == WM_IME_CHAR || msg == WM_IME_COMPOSITION || msg == WM_INPUTLANGCHANGE ||
                                   (msg == WM_INPUT && _logged < 300)))
            {
                _logged++;
                string extra = msg == WM_CHAR || msg == WM_IME_CHAR || msg == WM_UNICHAR ? $" char U+{(int)w:X4} '{(char)(int)w}'" : "";
                Log($"{DateTime.Now:HH:mm:ss.fff} msg {msg:X3} w {(long)w:X} l {(long)l:X}{extra} layout {GetKeyboardLayout(0):X}");
            }
            return CallWindowProcW(_oldProc, h, msg, w, l);
        }

        // ---------- memory scan for the test names ----------
        static readonly string[] Needles = { "Zqzq", "Xjxj", "zqzq", "xjxj" };

        static void ScanMemory()
        {
            Log($"--- F10 scan {DateTime.Now:HH:mm:ss}");
            var proc = GetCurrentProcess();
            long addr = 0, hits = 0;
            var pats = new List<(string, byte[])>();
            foreach (var n in Needles)
            {
                pats.Add((n + " ascii", Encoding.ASCII.GetBytes(n)));
                pats.Add((n + " utf16", Encoding.Unicode.GetBytes(n)));
            }
            while (addr < 0x7FFF_FFFF_FFFF && hits < 200)
            {
                if (VirtualQuery((IntPtr)addr, out var mbi, (UIntPtr)Marshal.SizeOf<MEMORY_BASIC_INFORMATION>()) == UIntPtr.Zero) break;
                long size = (long)mbi.RegionSize;
                bool ok = mbi.State == 0x1000 /*COMMIT*/ && (mbi.Protect & 0x04 /*RW*/ ) != 0 && (mbi.Protect & 0x100) == 0;
                if (ok && size < 512L * 1024 * 1024)
                {
                    var buf = new byte[size];
                    if (ReadProcessMemory(proc, mbi.BaseAddress, buf, (IntPtr)size, out _))
                    {
                        foreach (var (name, p) in pats)
                        {
                            for (int i = IndexOf(buf, p, 0); i >= 0 && hits < 200; i = IndexOf(buf, p, i + 1))
                            {
                                hits++;
                                long a = (long)mbi.BaseAddress + i;
                                int s0 = Math.Max(0, i - 48), s1 = Math.Min(buf.Length, i + 80);
                                Log($"hit {name} @ {a:X} (region {(long)mbi.BaseAddress:X} size {size:X})");
                                Log("  " + BitConverter.ToString(buf, s0, s1 - s0).Replace("-", " "));
                            }
                        }
                    }
                }
                addr = (long)mbi.BaseAddress + Math.Max(size, 0x1000);
            }
            Log($"--- scan done, {hits} hits");
        }

        static int IndexOf(byte[] hay, byte[] needle, int start)
        {
            for (int i = start; i <= hay.Length - needle.Length; i++)
            {
                if (hay[i] != needle[0]) continue;
                int k = 1;
                while (k < needle.Length && hay[i + k] == needle[k]) k++;
                if (k == needle.Length) return i;
            }
            return -1;
        }

        // ---------- Win32 ----------
        delegate bool EnumProc(IntPtr h, IntPtr l);
        [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
        [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
        [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassNameW(IntPtr h, StringBuilder sb, int n);
        [DllImport("user32.dll")] static extern IntPtr SetWindowLongPtrW(IntPtr h, int idx, IntPtr v);
        [DllImport("user32.dll")] static extern IntPtr CallWindowProcW(IntPtr prev, IntPtr h, uint msg, IntPtr w, IntPtr l);
        [DllImport("user32.dll")] static extern IntPtr GetKeyboardLayout(uint thread);
        [DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
        [DllImport("kernel32.dll")] static extern UIntPtr VirtualQuery(IntPtr a, out MEMORY_BASIC_INFORMATION m, UIntPtr len);
        [DllImport("kernel32.dll")] static extern bool ReadProcessMemory(IntPtr p, IntPtr a, byte[] buf, IntPtr n, out IntPtr read);

        [StructLayout(LayoutKind.Sequential)]
        struct MEMORY_BASIC_INFORMATION
        {
            public IntPtr BaseAddress, AllocationBase;
            public uint AllocationProtect;
            public ushort PartitionId;
            public UIntPtr RegionSize;
            public uint State, Protect, Type;
        }
    }
}
