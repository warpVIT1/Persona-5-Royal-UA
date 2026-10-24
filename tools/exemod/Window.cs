// Subclasses the game window so the mod sees keyboard messages (WM_KEYDOWN / WM_CHAR).
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

namespace P5RUkr
{
    public static class Window
    {
        public static event Action<uint, IntPtr> OnMessage;

        static IntPtr _oldProc;
        static WndProc _proc;   // keep the delegate alive

        public static void Hook()
        {
            new Thread(() =>
            {
                var pid = (uint)Environment.ProcessId;
                for (int i = 0; i < 2400; i++)
                {
                    IntPtr found = IntPtr.Zero;
                    EnumWindows((h, _) =>
                    {
                        GetWindowThreadProcessId(h, out var p);
                        if (p != pid || !IsWindowVisible(h)) return true;
                        var cls = new StringBuilder(256);
                        GetClassNameW(h, cls, 256);
                        if (cls.ToString() == "ConsoleWindowClass") return true;   // Reloaded console
                        GetWindowRect(h, out var r);
                        if (r.Right - r.Left < 320 || r.Bottom - r.Top < 200) return true;
                        found = h;
                        return false;
                    }, IntPtr.Zero);
                    if (found != IntPtr.Zero)
                    {
                        _proc = Proc;
                        _oldProc = SetWindowLongPtrW(found, -4 /*GWLP_WNDPROC*/, Marshal.GetFunctionPointerForDelegate(_proc));
                        Mod.Log($"window hooked {found:X}");
                        return;
                    }
                    Thread.Sleep(500);
                }
                Mod.Log("game window not found");
            }) { IsBackground = true }.Start();
        }

        static IntPtr Proc(IntPtr h, uint msg, IntPtr w, IntPtr l)
        {
            if (msg == 0x100 || msg == 0x102)
                try { OnMessage?.Invoke(msg, w); } catch { }
            return CallWindowProcW(_oldProc, h, msg, w, l);
        }

        delegate IntPtr WndProc(IntPtr h, uint msg, IntPtr w, IntPtr l);
        delegate bool EnumProc(IntPtr h, IntPtr l);

        [StructLayout(LayoutKind.Sequential)] struct RECT { public int Left, Top, Right, Bottom; }

        [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
        [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
        [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
        [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr h, out RECT r);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassNameW(IntPtr h, StringBuilder sb, int n);
        [DllImport("user32.dll")] static extern IntPtr SetWindowLongPtrW(IntPtr h, int idx, IntPtr v);
        [DllImport("user32.dll")] static extern IntPtr CallWindowProcW(IntPtr prev, IntPtr h, uint msg, IntPtr w, IntPtr l);
    }
}
