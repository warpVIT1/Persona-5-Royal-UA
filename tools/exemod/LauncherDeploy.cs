// Keeps a copy of the Steam "Play" launcher (tools/launcher) in a fixed place, so every player can use the same
// Steam launch options regardless of where Reloaded-II and the mod are installed:
//   cmd /c ""%LOCALAPPDATA%\P5R_UA\launcher\P5R_UA_Launcher.exe" %command%"
// The copy is refreshed whenever the mod ships a different launcher.
using System;
using System.IO;
using System.Linq;

namespace P5RUkr
{
    public static class LauncherDeploy
    {
        public static void Run(string modDir)
        {
            var src = Path.Combine(modDir, "launcher");
            if (!Directory.Exists(src)) return;
            var dst = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "P5R_UA", "launcher");
            Directory.CreateDirectory(dst);
            int n = 0;
            foreach (var f in Directory.GetFiles(src).Where(f => !f.EndsWith(".txt", StringComparison.OrdinalIgnoreCase)))
            {
                var d = Path.Combine(dst, Path.GetFileName(f));
                if (File.Exists(d) && File.ReadAllBytes(d).AsSpan().SequenceEqual(File.ReadAllBytes(f))) continue;
                try { File.Copy(f, d, true); n++; } catch { }   // the launcher may be running right now: next time
            }
            if (n > 0) Mod.Log($"launcher: {n} files -> {dst}");
        }
    }
}
