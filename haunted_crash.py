"""
Haunted Crash Simulator — Hybrid Version
- Default: Safe Tkinter-only illusion (no system-level changes).
- Optional: If you run as Administrator and have 'keyboard' installed,
  the script will attempt to block the Windows key temporarily.
  
Exit/Recovery:
- Secret exit combo: Ctrl+Shift+Q (always works while the app has focus).
- If using optional keyboard blocking, the script ensures keys are unblocked on exit.
  
WARNING: Do not use on machines you don't own or on shared/work computers.
"""

import tkinter as tk
import time
import threading
import sys
import os
from tkinter import ttk

# Optional system-level key blocking (requires admin and 'keyboard' lib)
try:
    import keyboard  # pip install keyboard
    HAS_KEYBOARD_LIB = True
except Exception:
    HAS_KEYBOARD_LIB = False

# ---------- Configuration ----------
BLOCK_WINDOWS_KEY = True  # Set to False if you don't want to attempt to block Win key
SECRET_EXIT_COMBO = ("<Control-Shift-KeyPress-q>")  # Controlled Tk binding exit
RESOLVE_DELAY = 2.0   # seconds of "attempting to resolve" before BSOD
AUTO_CLOSE_AFTER = None  # seconds to auto-close the program after BSOD; None => manual
# -----------------------------------

if not HAS_KEYBOARD_LIB:
    BLOCK_WINDOWS_KEY = False  # can't block if lib isn't available

# Helper to attempt safe blocking of Windows key (temporary)
def try_block_windows_key():
    if not BLOCK_WINDOWS_KEY:
        return False
    try:
        # keyboard.block_key works on Windows; requires admin
        keyboard.block_key('windows')
        keyboard.block_key('left windows')
        keyboard.block_key('right windows')
        # Also attempt to suppress the menu/application key
        keyboard.block_key('apps')
        return True
    except Exception as e:
        print("Could not block Windows key (requires admin):", e)
        return False

def try_unblock_windows_key():
    if not BLOCK_WINDOWS_KEY or not HAS_KEYBOARD_LIB:
        return
    try:
        keyboard.unblock_key('windows')
        keyboard.unblock_key('left windows')
        keyboard.unblock_key('right windows')
        keyboard.unblock_key('apps')
        keyboard.unhook_all()
    except Exception as e:
        print("Error while unblocking keys:", e)

# The main GUI class
class HauntedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Error")
        self.root.geometry("600x250")
        self.root.resizable(False, False)
        # prevent alt+f4 from closing (Tk will still try; we override protocol)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        self._setup_main_window()

        # Keep track whether we already moved to BSOD
        self.bsod_shown = False

        # Bind the secret exit combo (works while the app has focus)
        self.root.bind(SECRET_EXIT_COMBO, self.secret_exit)

        # Intercept common keys via Tk (these will be ignored)
        for seq in ("<Escape>", "<Alt-F4>", "<Control-w>", "<Control-W>"):
            self.root.bind_all(seq, lambda e: "break")

        # Hide cursor when fullscreen/BSOD shows
        self.normal_cursor = ""
        self.fake_cursor = "none"

    def _setup_main_window(self):
        # initial friendly-looking error dialog
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        lbl = tk.Label(frame, text="This program has crushed.", font=("Segoe UI", 18))
        lbl.pack(pady=(10,6))

        sub = tk.Label(frame, text="Please click 'Resolve' to attempt recovery.", font=("Segoe UI", 11))
        sub.pack(pady=(0,12))

        resolve_btn = tk.Button(frame, text="Resolve", width=12, command=self.start_resolve,
                                bg="#c62828", fg="white", font=("Segoe UI", 12, "bold"))
        resolve_btn.pack(pady=10)

        hint = tk.Label(frame, text="(Secret exit: Ctrl+Shift+Q)", font=("Segoe UI", 9), fg="gray")
        hint.pack(side="bottom", pady=(10,0))

    def start_resolve(self):
        # replace contents with a suspenseful resolving animation, then BSOD
        for w in self.root.winfo_children():
            w.destroy()

        self.root.geometry("700x300")
        center = tk.Frame(self.root, padx=20, pady=20)
        center.pack(fill="both", expand=True)

        lbl = tk.Label(center, text="Attempting to resolve...", font=("Segoe UI", 16))
        lbl.pack(pady=(20,10))

        pb = ttk.Progressbar(center, orient="horizontal", mode="determinate", maximum=100, length=500)
        pb.pack(pady=10)
        self.root.update()

        # use a thread so UI remains responsive to secret exit combo
        def animate_and_show():
            start = time.time()
            duration = RESOLVE_DELAY
            steps = 30
            for i in range(steps):
                # linear-ish progress with slight jitter
                progress = int((i+1)/steps * 100)
                pb['value'] = progress
                self.root.update()
                time.sleep(duration/steps)
            time.sleep(0.2)
            self.show_bsod()
        t = threading.Thread(target=animate_and_show, daemon=True)
        t.start()

    def show_bsod(self):
        if self.bsod_shown:
            return
        self.bsod_shown = True

        # Attempt to block Windows key (optional & best-effort)
        blocked = try_block_windows_key()
        if blocked:
            print("Windows key blocking active (temporary).")
        else:
            if BLOCK_WINDOWS_KEY:
                print("Wanted to block Win key but failed (not admin or unsupported).")

        # Make the window fullscreen and blue
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#0000AA")
        # hide cursor
        self.root.config(cursor=self.fake_cursor)
        # remove window decorations if possible (already fullscreen)
        # create BSOD text
        bsod_text = (
            "A problem has been detected and Windows has been shut down to prevent damage\n"
            "to your computer.\n\n"
            "The problem seems to be caused by the following file: HALLOWEEN.SYS\n\n"
            "CRITICAL_PROCESS_DIED\n\n"
            "If this is the first time you've seen this Stop error screen,\n"
            "restart your computer. If this screen appears again, follow\n"
            "these steps:\n\n"
            "Check to make sure any new hardware or software is properly installed.\n"
            "If this is a new installation, ask your hardware or software manufacturer\n"
            "for any Windows updates you might need.\n\n"
            "Technical information:\n\n"
            "*** STOP: 0x000000EF (0x0000000000000000, 0x0000000000000000)\n"
            "*** HALLOWEEN.SYS - Address FEA0:DEAD referenced memory at 0x00000000\n"
        )
        for w in self.root.winfo_children():
            w.destroy()

        label = tk.Label(self.root, text=bsod_text, fg="white", bg="#0000AA",
                         font=("Consolas", 14), justify="left", anchor="nw")
        label.pack(fill="both", expand=True, padx=60, pady=60)

        # Bind very few inputs; still listen for secret exit combo
        self.root.bind_all("<Alt-F4>", lambda e: "break")
        self.root.bind_all("<Escape>", lambda e: "break")
        # ensure secret exit remains
        self.root.bind(SECRET_EXIT_COMBO, self.secret_exit)

        # Optionally set a timer to auto-close (for demos)
        if AUTO_CLOSE_AFTER:
            def auto_close():
                time.sleep(AUTO_CLOSE_AFTER)
                self.cleanup_and_exit()
            threading.Thread(target=auto_close, daemon=True).start()

    def secret_exit(self, event=None):
        # restore everything and quit
        self.cleanup_and_exit()

    def cleanup_and_exit(self):
        try_unblock_windows_key()
        # restore cursor before exit
        try:
            self.root.config(cursor=self.normal_cursor)
        except Exception:
            pass
        # if fullscreen, try to cancel it
        try:
            self.root.attributes("-fullscreen", False)
        except Exception:
            pass
        # destroy and exit
        try:
            self.root.destroy()
        except Exception:
            pass
        # on some systems, exit the interpreter
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

# Entrypoint
def main():
    root = tk.Tk()
    app = HauntedApp(root)
    # Focus grabs to make escape less obvious
    try:
        root.focus_force()
        root.grab_set()  # grabs input to the app while it exists
    except Exception:
        pass

    # If user wants blocking but keyboard lib missing, warn them
    if BLOCK_WINDOWS_KEY and not HAS_KEYBOARD_LIB:
        print("BLOCK_WINDOWS_KEY requested but 'keyboard' library not available. "
              "Install with: pip install keyboard (and run as Administrator).")

    # Run
    try:
        root.mainloop()
    finally:
        # Ensure unblock in case of crash
        try_unblock_windows_key()

if __name__ == "__main__":
    main()
