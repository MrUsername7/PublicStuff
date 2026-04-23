import pygame
import sys
import time
import os
import numpy as np

_start_time = time.time()

def ticks_ms():
    return int((time.time() - _start_time) * 1000)

def ticks_us():
    return int((time.time() - _start_time) * 1_000_000)

pygame.init()

pygame.mixer.init(frequency=44100, size=-16, channels=1)

_clock = pygame.time.Clock()
FPS = 50

# =========================================================
# INTERNAL + DISPLAY RESOLUTION
# =========================================================
INTERNAL_W, INTERNAL_H = 128, 128
WINDOW_SCALE = 2  # 128 * 2 = 256

if not __name__ == "__main__":
    _screen = pygame.Surface((INTERNAL_W, INTERNAL_H))
    _window = pygame.display.set_mode((INTERNAL_W * WINDOW_SCALE, INTERNAL_H * WINDOW_SCALE))
    pygame.display.set_caption("Bit Emulator")

_clock = pygame.time.Clock()
_start_time = time.time()

RGB565 = 1

# =========================================================
# COLORS
# =========================================================
class Display:
    class Color:
        Black  = (0, 0, 0)
        White  = (255, 255, 255)
        Red    = (255, 0, 0)
        Maroon = (128, 0, 0)
        Green  = (0, 255, 0)
        Forest = (0, 128, 0)
        Blue   = (0, 0, 255)
        Navy   = (0, 0, 128)
        Cyan   = (0, 255, 255)
        Yellow = (255, 255, 0)
        Purple = (128, 0, 128)
        Gray   = (128, 128, 128)

def _resolve_color(color):
    if color is None:
        raise TypeError("can't convert NoneType to int")

    # hardware palette mode
    if isinstance(color, int):
        v = color & 31
        return (0, 0, int(v * 255 / 31))

    return color

def _tint(surface, color):
    surf = surface.copy()
    surf = surf.convert_alpha()

    # =====================================================
    # HARDWARE MODE: 0–31 blue scale
    # =====================================================
    if isinstance(color, int):
        v = max(0, min(31, color))
        b = int(v * 255 / 31)
        tint = (0, 0, b, 255)

    # =====================================================
    # RGB MODE
    # =====================================================
    else:
        r, g, b = color
        tint = (r, g, b, 255)

    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill(tint)

    surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return surf

# =========================================================
# GLOBAL CACHE
# =========================================================
PNG_CACHE = {}
FONT_SURFACE = None

# =========================================================
# DISPLAY WRAPPER
# =========================================================
class DisplayWrapper:

    def fill(self, color):
        _screen.fill(color)

    def pixel(self, x, y, color):
        _screen.set_at((x, y), color)

    def commit(self):
        scaled = pygame.transform.scale(_screen, _window.get_size())
        _window.blit(scaled, (0, 0))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        _clock.tick(FPS)

    def text(self, string, x, y, color):
        cx = x

        def _resolve_color(color):
            if color is None:
                raise TypeError("can't convert NoneType to int")

            if isinstance(color, int):
                v = color & 31
                return v  # <-- IMPORTANT: return INT, not RGB

            return color

        color = _resolve_color(color)

        for ch in str(string):
            code = ord(ch)

            # =====================================================
            # UNICODE WIDTH RULE
            # =====================================================

            if code <= 0x1F:
                img = _load_png("checker.png")
                if img:
                    img = pygame.transform.scale(img, (8, 8))
                    img = _tint(img, color)
                    _screen.blit(img, (cx, y))
                cx += 8
                continue

            elif 0x80 <= code < 0x800:
                img = _load_png("checker.png")
                if img:
                    img = pygame.transform.scale(img, (8, 8))
                    img = _tint(img, color)
                    _screen.blit(img, (cx, y))
                    _screen.blit(img, (cx + 8, y))
                cx += 16
                continue

            elif code >= 0x800:
                img = _load_png("checker.png")
                if img:
                    img = pygame.transform.scale(img, (8, 8))
                    img = _tint(img, color)
                    _screen.blit(img, (cx, y))
                    _screen.blit(img, (cx + 8, y))
                    _screen.blit(img, (cx + 16, y))
                cx += 24
                continue

            # =====================================================
            # NORMAL ASCII + SPECIAL MAP
            # =====================================================

            special_map = {
                "\\": "backslash.png",
                "/": "slash.png",
                ":": "colon.png",
                "*": "star.png",
                "?": "question.png",
                "\"": "quotation.png",
                "<": "larrow.png",
                ">": "rarrow.png",
                "|": "bar.png",
                " ": None
            }

            if ch == " ":
                cx += 8
                continue

            img = None

            if ch in special_map and special_map[ch]:
                img = _load_png(special_map[ch])
            else:
                if ch.islower():
                    img = _load_png(f"{ch}2.png")
                if not img:
                    img = _load_png(f"{ch.upper()}.png")
                if not img:
                    img = _load_png(f"{ch}.png")

            if img:
                img = pygame.transform.scale(img, (8, 8))
                img = _tint(img, color)
                _screen.blit(img, (cx, y))
            else:
                fallback = _load_png("checker.png")
                if fallback:
                    fallback = pygame.transform.scale(fallback, (8, 8))
                    fallback = _tint(fallback, color)
                    _screen.blit(fallback, (cx, y))

            cx += 8

    def sprite(self, sprite, x, y):
        if hasattr(sprite, "surface"):
            _screen.blit(sprite.surface, (x, y))
    def blit(self, sprite, x, y, transparency=0):
        if not hasattr(sprite, "surface"):
            return

        surf = sprite.surface

        # =====================================================
        # NORMAL MODE
        # =====================================================
        if transparency != 16384:
            _screen.blit(surf, (x, y))
            return

        # =====================================================
        # MASK MODE (0x400000 = skip pixel)
        # =====================================================
        w, h = surf.get_size()

        for iy in range(h):
            for ix in range(w):

                px = surf.get_at((ix, iy))

                # convert to RGB888 int for exact match
                rgb = (px[0] << 16) | (px[1] << 8) | px[2]

                if rgb == 0x400000:
                    continue

                _screen.set_at((x + ix, y + iy), px[:3])

    def rect(self, x, y, w, h, color, filled=True):
        color = _resolve_color(color)
        if filled:
            pygame.draw.rect(_screen, color, pygame.Rect(x, y, w, h))
        else:
            pygame.draw.rect(_screen, color, pygame.Rect(x, y, w, h), 1)

    def line(self, x1, y1, x2, y2, color):
        color = _resolve_color(color)
        pygame.draw.line(_screen, color, (x1, y1), (x2, y2))

    def ellipse(self, x, y, rx, ry, color, filled=True):
        color = _resolve_color(color)
        rect = pygame.Rect(x - rx, y - ry, rx * 2, ry * 2)

        if filled:
            pygame.draw.ellipse(_screen, color, rect)
        else:
            pygame.draw.ellipse(_screen, color, rect, 1)

display = DisplayWrapper()

# =========================================================
# PNG LOADER (RGB565 sprites etc)
# =========================================================
def _load_png(name):
    path = os.path.join(os.getcwd(), "font", name)

    if path in PNG_CACHE:
        return PNG_CACHE[path]

    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        PNG_CACHE[path] = img
        return img

    return None

# =========================================================
# FRAMEBUFFER (RGB565 SPRITES)
# =========================================================
class FrameBuffer:
    def __init__(self, buffer, width, height, fmt=None):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

        if buffer and fmt == RGB565:
            self._decode(buffer)

    def _decode(self, buffer):
        i = 0
        for y in range(self.height):
            for x in range(self.width):
                if i + 1 >= len(buffer):
                    return

                c = buffer[i] << 8 | buffer[i + 1]
                i += 2

                # =========================================
                # TRANSPARENT PIXEL (REAL HW BEHAVIOR)
                # =========================================
                if c == 0x0000:
                    # leave pixel transparent (do nothing)
                    continue

                r = ((c >> 11) & 0x1F) << 3
                g = ((c >> 5) & 0x3F) << 2
                b = (c & 0x1F) << 3

                self.surface.set_at((x, y), (r, g, b, 255))

# =========================================================
# BUTTONS
# =========================================================
class Buttons:
    Up    = pygame.K_w
    Left  = pygame.K_a
    Down  = pygame.K_s
    Right = pygame.K_d

    A     = pygame.K_q
    B     = pygame.K_e
    C     = pygame.K_r

_keys = pygame.key.get_pressed()
_prev_keys = _keys

class ButtonHandler:
    def __init__(self):
        self.press = {}
        self.release = {}

    def on_press(self, key, func):
        self.press[key] = func

    def on_release(self, key, func):
        self.release[key] = func

    def scan(self):
        global _keys, _prev_keys
        _prev_keys = _keys
        _keys = pygame.key.get_pressed()
        pygame.event.pump()

        for k, f in self.press.items():
            if _keys[k] and not _prev_keys[k]:
                f()

        for k, f in self.release.items():
            if not _keys[k] and _prev_keys[k]:
                f()

    def state(self, btn):
        return _keys[btn] if _keys is not None else False

buttons = ButtonHandler()

def button_state(btn):
    return _keys[btn]

# =========================================================
# TIMING
# =========================================================
import time as _pytime

class _Time:
    _start_time = _pytime.time()

    @staticmethod
    def ticks_ms():
        return int((_pytime.time() - _Time._start_time) * 1000)

    @staticmethod
    def ticks_us():
        return int((_pytime.time() - _Time._start_time) * 1_000_000)

    @staticmethod
    def sleep(seconds):
        _pytime.sleep(seconds)

    @staticmethod
    def sleep_ms(ms):
        _pytime.sleep(ms / 1000.0)

# 🔥 THIS LINE FIXES YOUR ERROR
time = _Time

# =========================================================
# BIT CORE
# =========================================================
class BitDevice:
    def begin(self):
        display.fill(Display.Color.Black)
        display.commit()
        print("Bit Emulator Ready")

Bit = BitDevice()

def begin():
    Bit.begin()

class Piezo:
    def tone(self, freq, duration_ms):
        import math, array, time

        sample_rate = 44100
        length = int(sample_rate * duration_ms / 1000)

        buf = array.array('h')

        for i in range(length):
            t = i / sample_rate
            val = 32767 if math.sin(2 * math.pi * freq * t) >= 0 else -32767
            buf.append(val)

        sound = pygame.mixer.Sound(buffer=buf)
        channel = sound.play()

        # 🔥 BLOCK like real hardware
        time.sleep(duration_ms / 1000.0)

        return

piezo = Piezo()

class Backlight:
    def __init__(self):
        self.enabled = True

    def on(self):
        self.enabled = True

    def off(self):
        self.enabled = False

backlight = Backlight()
if not backlight.enabled:
    _screen.fill((0, 0, 0))

def emulatedCheck():
    return True

# =========================================================
# MICRO-PYTHON MODULE SHADOWING
# =========================================================

import types
import sys

# --- TIME MODULE (shadow) ---
time = types.ModuleType("time")
time.ticks_ms = _Time.ticks_ms
time.ticks_us = _Time.ticks_us
time.sleep = _Time.sleep
time.sleep_ms = _Time.sleep_ms

# --- FRAMEBUF MODULE (shadow) ---
framebuf = types.ModuleType("framebuf")
framebuf.FrameBuffer = FrameBuffer
framebuf.RGB565 = RGB565

# inject into python import system
sys.modules["time"] = time
sys.modules["framebuf"] = framebuf
