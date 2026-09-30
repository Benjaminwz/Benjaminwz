"""連點器核心邏輯（不依賴 GUI，方便測試）。"""
import random
import threading
import time
from dataclasses import dataclass


@dataclass
class Config:
    interval_ms: float = 100.0   # 每次點擊間隔（毫秒）
    jitter_pct: float = 0.0      # 隨機抖動百分比 0~100，讓間隔不那麼規律
    button: str = "left"         # left / right / middle
    double: bool = False         # 是否每次雙擊
    hold: bool = False           # 按住模式：按下不放（適合蓄力、採集）
    max_clicks: int = 0          # 0 = 無限
    start_delay_s: float = 3.0   # 開始前倒數秒數，讓你切回遊戲

    def validate(self):
        if self.button not in ("left", "right", "middle"):
            raise ValueError("按鍵必須是 left / right / middle")
        if self.interval_ms < 1:
            raise ValueError("間隔至少 1 毫秒")
        if not 0 <= self.jitter_pct <= 100:
            raise ValueError("抖動必須在 0~100 之間")
        if self.max_clicks < 0 or self.start_delay_s < 0:
            raise ValueError("次數與延遲不可為負數")


class PynputBackend:
    """真正送出滑鼠事件（延遲載入，沒有桌面環境時不會在 import 就壞掉）。"""

    def __init__(self):
        from pynput.mouse import Button, Controller
        self._ctl = Controller()
        self._buttons = {"left": Button.left, "right": Button.right,
                         "middle": Button.middle}

    def click(self, button, count=1):
        self._ctl.click(self._buttons[button], count)

    def press(self, button):
        self._ctl.press(self._buttons[button])

    def release(self, button):
        self._ctl.release(self._buttons[button])


class Clicker:
    def __init__(self, backend, config, on_tick=None, on_stop=None,
                 sleep=time.sleep):
        config.validate()
        self.backend, self.cfg = backend, config
        self.on_tick, self.on_stop = on_tick, on_stop
        self._sleep = sleep
        self._stop = threading.Event()
        self._thread = None
        self.clicks = 0

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.running:
            return
        self._stop.clear()
        self.clicks = 0
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def join(self, timeout=None):
        if self._thread:
            self._thread.join(timeout)

    def next_delay(self):
        base = self.cfg.interval_ms / 1000.0
        j = self.cfg.jitter_pct / 100.0
        return max(0.001, base * (1 + random.uniform(-j, j)))

    def run(self):
        c = self.cfg
        try:
            # 可中斷的開始倒數
            if self._stop.wait(c.start_delay_s):
                return
            if c.hold:
                self.backend.press(c.button)
                self._stop.wait()
                return
            while not self._stop.is_set():
                self.backend.click(c.button, 2 if c.double else 1)
                self.clicks += 1
                if self.on_tick:
                    self.on_tick(self.clicks)
                if c.max_clicks and self.clicks >= c.max_clicks:
                    break
                if self._stop.wait(self.next_delay()):
                    break
        finally:
            if c.hold:
                self.backend.release(c.button)  # 保證放開，避免滑鼠卡住
            if self.on_stop:
                self.on_stop(self.clicks)
