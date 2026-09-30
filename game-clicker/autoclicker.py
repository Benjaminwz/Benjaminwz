"""遊戲連點器 — 圖形介面。執行：python autoclicker.py"""
import tkinter as tk
from tkinter import ttk, messagebox

from clicker_core import Clicker, Config, PynputBackend

HOTKEY_CHOICES = ["F6", "F7", "F8", "F9", "F10", "F12"]
BUTTONS = {"左鍵": "left", "右鍵": "right", "中鍵": "middle"}


class App:
    def __init__(self, root):
        self.root = root
        root.title("遊戲連點器")
        root.resizable(False, False)
        self.clicker = None
        self.backend = None
        self.listener = None

        self.v_ms = tk.StringVar(value="100")
        self.v_jit = tk.StringVar(value="10")
        self.v_btn = tk.StringVar(value="左鍵")
        self.v_max = tk.StringVar(value="0")
        self.v_delay = tk.StringVar(value="3")
        self.v_double = tk.BooleanVar(value=False)
        self.v_hold = tk.BooleanVar(value=False)
        self.v_key = tk.StringVar(value="F6")
        self.v_status = tk.StringVar(value="待命 — 按熱鍵或按鈕開始")

        f = ttk.Frame(root, padding=14)
        f.grid()
        rows = [
            ("點擊間隔（毫秒）", ttk.Spinbox(f, from_=1, to=600000, width=10, textvariable=self.v_ms)),
            ("隨機抖動 %（0=固定）", ttk.Spinbox(f, from_=0, to=100, width=10, textvariable=self.v_jit)),
            ("滑鼠按鍵", ttk.Combobox(f, values=list(BUTTONS), width=8, state="readonly", textvariable=self.v_btn)),
            ("點擊次數（0=無限）", ttk.Spinbox(f, from_=0, to=10**9, width=10, textvariable=self.v_max)),
            ("開始前倒數（秒）", ttk.Spinbox(f, from_=0, to=60, width=10, textvariable=self.v_delay)),
            ("開始／停止熱鍵", ttk.Combobox(f, values=HOTKEY_CHOICES, width=8, state="readonly", textvariable=self.v_key)),
        ]
        for i, (label, w) in enumerate(rows):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", pady=3)
            w.grid(row=i, column=1, sticky="e", pady=3, padx=(12, 0))
        self.v_key.trace_add("write", lambda *_: self.bind_hotkey())

        ttk.Checkbutton(f, text="雙擊", variable=self.v_double).grid(row=6, column=0, sticky="w")
        ttk.Checkbutton(f, text="按住不放（蓄力／採集）", variable=self.v_hold).grid(row=6, column=1, sticky="w")

        self.btn = ttk.Button(f, text="開始", command=self.toggle)
        self.btn.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(12, 4), ipady=6)
        ttk.Label(f, textvariable=self.v_status, foreground="#555").grid(row=8, column=0, columnspan=2)
        ttk.Label(f, text="提示：開始後把游標移到遊戲內目標位置；\n連點會點在游標目前所在處。",
                  foreground="#888", justify="left").grid(row=9, column=0, columnspan=2, pady=(8, 0))

        try:
            self.backend = PynputBackend()
        except Exception as e:  # 缺套件或沒有桌面權限
            messagebox.showerror("無法初始化滑鼠控制", f"請先執行 pip install -r requirements.txt\n\n{e}")
        self.bind_hotkey()
        root.protocol("WM_DELETE_WINDOW", self.quit)

    # ---- 熱鍵 ----
    def bind_hotkey(self):
        try:
            from pynput import keyboard
        except Exception:
            return
        if self.listener:
            self.listener.stop()
        key = getattr(keyboard.Key, self.v_key.get().lower())
        self.listener = keyboard.Listener(
            on_press=lambda k: k == key and self.root.after(0, self.toggle))
        self.listener.daemon = True
        self.listener.start()

    # ---- 控制 ----
    def read_config(self):
        return Config(
            interval_ms=float(self.v_ms.get()),
            jitter_pct=float(self.v_jit.get()),
            button=BUTTONS[self.v_btn.get()],
            double=self.v_double.get(),
            hold=self.v_hold.get(),
            max_clicks=int(self.v_max.get()),
            start_delay_s=float(self.v_delay.get()),
        )

    def toggle(self):
        if self.clicker and self.clicker.running:
            self.clicker.stop()
            return
        if not self.backend:
            return
        try:
            self.clicker = Clicker(
                self.backend, self.read_config(),
                on_tick=lambda n: self.root.after(0, self.v_status.set, f"連點中… 已點 {n} 次"),
                on_stop=lambda n: self.root.after(0, self.stopped, n))
        except ValueError as e:
            messagebox.showwarning("設定有誤", str(e))
            return
        self.btn.config(text=f"停止（{self.v_key.get()}）")
        d = self.clicker.cfg.start_delay_s
        self.v_status.set(f"{d:g} 秒後開始，請切回遊戲" if d else "連點中…")
        self.clicker.start()

    def stopped(self, n):
        self.btn.config(text="開始")
        self.v_status.set(f"已停止 — 共點擊 {n} 次")

    def quit(self):
        if self.clicker:
            self.clicker.stop()
            self.clicker.join(1)
        if self.listener:
            self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
