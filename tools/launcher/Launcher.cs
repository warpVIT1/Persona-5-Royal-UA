// Starts Persona 5 Royal with Reloaded-II mods from Steam's "Play" button, without the Reloaded window.
//
// Steam launch options:   "<path>\P5R_UA_Launcher.exe" %command%
// Steam then runs this program with the game's command line. It starts the game suspended, loads Reloaded's
// bootstrapper into it (the same way Reloaded-II itself does: LoadLibraryW in a remote thread; the path comes from
// %APPDATA%\Reloaded-Mod-Loader-II\ReloadedII.json), resumes the game and exits.
// (Reloaded's "Deploy ASI Loader" hangs P5R on a black screen, even with no mods enabled.)
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;

namespace P5RUkrLauncher
{
    static class Program
    {
        static string _log;

        static int Main(string[] args)
        {
            _log = Path.Combine(AppContext.BaseDirectory, "launcher_log.txt");
            File.WriteAllText(_log, $"=== {DateTime.Now:yyyy-MM-dd HH:mm:ss}{Environment.NewLine}");
            try { return Run(args); }
            catch (Exception e) { Log("error: " + e); return 1; }
        }

        static void Log(string s) { try { File.AppendAllText(_log, s + Environment.NewLine); } catch { } }

        static int Run(string[] args)
        {
            // the game: first argument that is an existing .exe (Steam passes %command% = "...\P5R.exe" [args])
            int gi = Array.FindIndex(args, a => a.EndsWith(".exe", StringComparison.OrdinalIgnoreCase) && File.Exists(a));
            if (gi < 0) { Log("game exe not found in arguments: " + string.Join(" ", args)); return 2; }
            string game = Path.GetFullPath(args[gi]);
            var rest = new StringBuilder();
            for (int i = gi + 1; i < args.Length; i++) rest.Append(" \"").Append(args[i]).Append('"');

            var cfg = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                                   "Reloaded-Mod-Loader-II", "ReloadedII.json");
            using var json = JsonDocument.Parse(File.ReadAllText(cfg));
            string boot = json.RootElement.GetProperty("Bootstrapper64Path").GetString();
            if (!File.Exists(boot)) { Log("Reloaded bootstrapper not found: " + boot); return 3; }
            Log($"game: {game}\nbootstrapper: {boot}");

            var si = new STARTUPINFO { cb = Marshal.SizeOf<STARTUPINFO>() };
            string cmd = $"\"{game}\"{rest}";
            if (!CreateProcessW(game, new StringBuilder(cmd), IntPtr.Zero, IntPtr.Zero, false, CREATE_SUSPENDED,
                                IntPtr.Zero, Path.GetDirectoryName(game), ref si, out var pi))
            { Log("CreateProcess failed: " + Marshal.GetLastWin32Error()); return 4; }

            var started = DateTime.Now.AddSeconds(-2);
            bool ok = Inject(pi.hProcess, boot);
            Log(ok ? "bootstrapper loaded" : "injection failed");
            // Reloaded sets up its mods asynchronously; the game may run only after that (the CRI file hook must be in
            // place before the game opens its archives). Reloaded-II's launcher waits too: wait for its log line.
            if (ok) Log(WaitForLoader(started) ? "mods loaded" : "timed out waiting for Reloaded, resuming anyway");
            ResumeThread(pi.hThread);
            CloseHandle(pi.hThread);
            CloseHandle(pi.hProcess);
            return ok ? 0 : 5;
        }

        // Reloaded writes "[Reloaded] Total Loader Initialization Time" to its newest P5R log when all mods are loaded
        static bool WaitForLoader(DateTime since)
        {
            var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                                   "Reloaded-Mod-Loader-II", "Logs");
            var until = DateTime.Now.AddSeconds(30);
            while (DateTime.Now < until)
            {
                try
                {
                    foreach (var f in new DirectoryInfo(dir).GetFiles("*P5R*.txt"))
                    {
                        if (f.LastWriteTime < since) continue;
                        using var s = new FileStream(f.FullName, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
                        using var r = new StreamReader(s);
                        if (r.ReadToEnd().Contains("Total Loader Initialization Time")) return true;
                    }
                }
                catch { }
                System.Threading.Thread.Sleep(100);
            }
            return false;
        }

        static bool Inject(IntPtr proc, string dll)
        {
            byte[] path = Encoding.Unicode.GetBytes(dll + "\0");
            IntPtr mem = VirtualAllocEx(proc, IntPtr.Zero, (UIntPtr)path.Length, 0x3000, 0x04);
            if (mem == IntPtr.Zero || !WriteProcessMemory(proc, mem, path, (UIntPtr)path.Length, out _)) return false;
            IntPtr load = GetProcAddress(GetModuleHandleW("kernel32.dll"), "LoadLibraryW");
            IntPtr th = CreateRemoteThread(proc, IntPtr.Zero, UIntPtr.Zero, load, mem, 0, out _);
            if (th == IntPtr.Zero) return false;
            WaitForSingleObject(th, 60000);
            GetExitCodeThread(th, out uint module);
            CloseHandle(th);
            return module != 0;
        }

        const uint CREATE_SUSPENDED = 0x4;

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        struct STARTUPINFO
        {
            public int cb; public string lpReserved, lpDesktop, lpTitle;
            public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
            public short wShowWindow, cbReserved2; public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
        }
        [StructLayout(LayoutKind.Sequential)]
        struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public int dwProcessId, dwThreadId; }

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        static extern bool CreateProcessW(string app, StringBuilder cmd, IntPtr pa, IntPtr ta, bool inherit, uint flags,
                                          IntPtr env, string dir, ref STARTUPINFO si, out PROCESS_INFORMATION pi);
        [DllImport("kernel32.dll")] static extern uint ResumeThread(IntPtr t);
        [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
        [DllImport("kernel32.dll")] static extern IntPtr VirtualAllocEx(IntPtr p, IntPtr a, UIntPtr s, uint t, uint pr);
        [DllImport("kernel32.dll")] static extern bool WriteProcessMemory(IntPtr p, IntPtr a, byte[] b, UIntPtr n, out UIntPtr w);
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode)] static extern IntPtr GetModuleHandleW(string n);
        [DllImport("kernel32.dll", CharSet = CharSet.Ansi)] static extern IntPtr GetProcAddress(IntPtr m, string n);
        [DllImport("kernel32.dll")] static extern IntPtr CreateRemoteThread(IntPtr p, IntPtr a, UIntPtr s, IntPtr start, IntPtr param, uint f, out uint id);
        [DllImport("kernel32.dll")] static extern uint WaitForSingleObject(IntPtr h, uint ms);
        [DllImport("kernel32.dll")] static extern bool GetExitCodeThread(IntPtr h, out uint code);
    }
}
