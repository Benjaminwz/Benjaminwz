import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from clicker_core import Clicker, Config  # noqa: E402


class Fake:
    def __init__(self):
        self.log = []

    def click(self, b, n=1):
        self.log.append(("click", b, n))

    def press(self, b):
        self.log.append(("press", b))

    def release(self, b):
        self.log.append(("release", b))


def cfg(**kw):
    kw.setdefault("interval_ms", 1)
    kw.setdefault("start_delay_s", 0)
    return Config(**kw)


class CoreTest(unittest.TestCase):
    def test_max_clicks(self):
        f = Fake()
        c = Clicker(f, cfg(max_clicks=5))
        c.run()
        self.assertEqual(c.clicks, 5)
        self.assertEqual(f.log, [("click", "left", 1)] * 5)

    def test_double_right(self):
        f = Fake()
        Clicker(f, cfg(max_clicks=2, double=True, button="right")).run()
        self.assertEqual(f.log, [("click", "right", 2)] * 2)

    def test_stop_from_thread(self):
        f = Fake()
        c = Clicker(f, cfg())
        c.start()
        while c.clicks < 3:
            pass
        c.stop()
        c.join(2)
        self.assertFalse(c.running)

    def test_hold_always_releases(self):
        f = Fake()
        c = Clicker(f, cfg(hold=True))
        c.start()
        while ("press", "left") not in f.log:
            pass
        c.stop()
        c.join(2)
        self.assertEqual(f.log, [("press", "left"), ("release", "left")])

    def test_stop_during_countdown_clicks_nothing(self):
        f = Fake()
        c = Clicker(f, cfg(start_delay_s=30))
        c.start()
        c.stop()
        c.join(2)
        self.assertEqual(f.log, [])

    def test_jitter_range(self):
        c = Clicker(Fake(), cfg(interval_ms=100, jitter_pct=20))
        for _ in range(200):
            self.assertTrue(0.079 <= c.next_delay() <= 0.121)

    def test_validate(self):
        for bad in (dict(interval_ms=0), dict(button="x"), dict(jitter_pct=101)):
            with self.assertRaises(ValueError):
                Clicker(Fake(), cfg(**bad))


if __name__ == "__main__":
    unittest.main()
