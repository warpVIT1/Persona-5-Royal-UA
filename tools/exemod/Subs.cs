// Ukrainian subtitles for the anime cutscenes.
//
// P5R.exe keeps every subtitle line as a UTF-8 C string and a table of 64-bit pointers to them
// (tools/scripts/subtitles.py). <mod>/subs.tsv lists: RVA of a pointer slot, RVA of the English string the slot
// must point to (checked, so another game version is left alone), and the Ukrainian line. The lines are copied
// into memory of our own and the slots are pointed at them. The game draws them with its own character table,
// so Ukrainian-only letters are already written as the characters at our glyph indices.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

namespace P5RUkr
{
    public static unsafe class Subs
    {
        public static void Start(string modDir)
        {
            var path = Path.Combine(modDir, "subs.tsv");
            if (!File.Exists(path)) return;
            long b = (long)Process.GetCurrentProcess().MainModule.BaseAddress;
            var rows = new List<(long slot, long str, byte[] text)>();
            foreach (var line in File.ReadAllLines(path, Encoding.UTF8))
            {
                var t = line.Split('\t');
                if (t.Length != 3) continue;
                var bytes = Encoding.UTF8.GetBytes(t[2] + "\0");
                rows.Add((long.Parse(t[0], NumberStyles.HexNumber), long.Parse(t[1], NumberStyles.HexNumber), bytes));
            }
            long total = 0;
            foreach (var r in rows) total += r.text.Length;
            long mem = (long)VirtualAlloc(IntPtr.Zero, (UIntPtr)total, 0x3000, 0x04);
            if (mem == 0) { Mod.Log("subs: no memory"); return; }
            int ok = 0, skip = 0;
            long cur = mem;
            foreach (var (slot, str, text) in rows)
            {
                long* p = (long*)(b + slot);
                if (*p != b + str) { skip++; continue; }   // not the English line we expect: leave it
                Marshal.Copy(text, 0, (IntPtr)cur, text.Length);
                VirtualProtect((IntPtr)p, (UIntPtr)8, 0x04, out var old);
                *p = cur;
                VirtualProtect((IntPtr)p, (UIntPtr)8, old, out _);
                cur += text.Length;
                ok++;
            }
            Mod.Log($"subs: {ok} subtitle lines replaced, {skip} skipped");
        }

        [DllImport("kernel32.dll")] static extern IntPtr VirtualAlloc(IntPtr a, UIntPtr size, uint type, uint protect);
        [DllImport("kernel32.dll")] static extern bool VirtualProtect(IntPtr a, UIntPtr size, uint prot, out uint old);
    }
}
