#!/usr/bin/env python3
"""Malachite Rally — neon pong/volley arcade for ElbowOS."""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys

import pygame

W, H = 1080, 1920
FPS = 30
TITLE = "MALACHITE RALLY"
HANDLE = "x.com/ElbowOS"
VOID = (4, 18, 16)
PINE = (8, 42, 36)
MOSS = (18, 72, 58)
JADE = (36, 210, 128)
MINT = (168, 255, 196)
GOLD = (255, 214, 72)
MAG = (255, 72, 168)
CYAN = (64, 236, 255)
PEARL = (236, 255, 248)
AMBER = (255, 176, 48)
PW, PH = 220, 28
BR = 18
MARGIN = 56
TOP_Y, BOT_Y = 280, 1640


class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, vx, vy, life, col, r=5):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life, self.col, self.r = life, col, r


class Orb:
    __slots__ = ("x", "y", "kind", "phase")

    def __init__(self, x, y, kind):
        self.x, self.y, self.kind, self.phase = x, y, kind, random.random() * math.tau


class Game:
    def __init__(self, record: bool):
        self.record = record
        self.surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.Font(None, 62)
        self.font_md = pygame.font.Font(None, 44)
        self.font_sm = pygame.font.Font(None, 28)
        self.score_p = self.score_a = 0
        self.reset_rally(serve=1)

    def reset_rally(self, serve: int) -> None:
        self.px = self.ax = W * 0.5
        self.bx = W * 0.5
        self.by = H * 0.5
        spd = 640
        self.bvx = random.choice((-1, 1)) * random.uniform(220, 380)
        self.bvy = serve * spd
        self.trail = []
        self.sparks: list[Spark] = []
        self.orbs: list[Orb] = [
            Orb(random.uniform(160, W - 160), random.uniform(620, 1280),
                random.choice(("boost", "curve")))
            for _ in range(3)
        ]
        self.flash = 0.0
        self.t = 0.0
        self.combo = 1
        self.stars = [[random.uniform(0, W), random.uniform(220, 1680),
                       random.uniform(1.0, 2.6)] for _ in range(70)]

    def burst(self, x, y, col, n=14) -> None:
        for _ in range(n):
            a = random.random() * math.tau
            spd = random.uniform(60, 380)
            self.sparks.append(Spark(x, y, math.cos(a) * spd, math.sin(a) * spd,
                                     random.uniform(0.16, 0.4), col, random.randint(3, 7)))

    def bounce_paddle(self, cx, y, going_up: bool) -> None:
        if abs(self.by - y) > PH * 0.7 + BR:
            return
        if abs(self.bx - cx) > PW * 0.5 + BR:
            return
        if going_up and self.bvy > 0:
            return
        if (not going_up) and self.bvy < 0:
            return
        off = (self.bx - cx) / (PW * 0.5)
        self.bvx = max(-720, min(720, self.bvx + off * 340 + random.uniform(-40, 40)))
        self.bvy = -abs(self.bvy) * 1.06 if going_up else abs(self.bvy) * 1.06
        self.bvy = max(-980, min(980, self.bvy))
        self.by = y + (PH * 0.5 + BR + 2) * (1 if going_up else -1)
        self.combo = min(9, self.combo + 1)
        self.score_p += 4 * self.combo if not going_up else 0
        self.score_a += 2 if going_up else 0
        self.burst(self.bx, self.by, MINT if not going_up else MAG, 16)
        self.flash = 0.08

    def autoplay(self) -> None:
        target_p = self.bx + self.bvx * 0.18
        target_a = self.bx + self.bvx * 0.12
        if self.bvy > 0:
            self.px += (target_p - self.px) * 0.22
        else:
            self.px += ((W * 0.5) - self.px) * 0.04
        if self.bvy < 0:
            self.ax += (target_a - self.ax) * 0.20
        else:
            self.ax += ((W * 0.5) - self.ax) * 0.04
        self.px = max(MARGIN + PW * 0.5, min(W - MARGIN - PW * 0.5, self.px))
        self.ax = max(MARGIN + PW * 0.5, min(W - MARGIN - PW * 0.5, self.ax))

    def handle(self, ev) -> None:
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
            self.score_p = self.score_a = 0
            self.reset_rally(serve=1)

    def update(self, dt: float) -> None:
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        keys = pygame.key.get_pressed() if not self.record else None
        if keys:
            spd = 720
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.px -= spd * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.px += spd * dt
            self.px = max(MARGIN + PW * 0.5, min(W - MARGIN - PW * 0.5, self.px))
        if self.record:
            self.autoplay()
        self.bx += self.bvx * dt
        self.by += self.bvy * dt
        if self.bx < MARGIN + BR:
            self.bx = MARGIN + BR
            self.bvx = abs(self.bvx) * 1.04
            self.burst(self.bx, self.by, CYAN, 10)
        elif self.bx > W - MARGIN - BR:
            self.bx = W - MARGIN - BR
            self.bvx = -abs(self.bvx) * 1.04
            self.burst(self.bx, self.by, CYAN, 10)
        self.bounce_paddle(self.px, BOT_Y, going_up=False)
        self.bounce_paddle(self.ax, TOP_Y, going_up=True)
        kept_orbs = []
        for o in self.orbs:
            o.phase += 3.4 * dt
            if math.hypot(self.bx - o.x, self.by - o.y) < 34 + BR:
                if o.kind == "boost":
                    self.bvy *= 1.18
                    self.burst(o.x, o.y, GOLD, 18)
                    self.score_p += 12
                else:
                    self.bvx += random.choice((-1, 1)) * 220
                    self.burst(o.x, o.y, AMBER, 18)
                    self.score_p += 8
                kept_orbs.append(Orb(random.uniform(160, W - 160),
                                     random.uniform(620, 1280),
                                     random.choice(("boost", "curve"))))
            else:
                kept_orbs.append(o)
        self.orbs = kept_orbs
        if self.by < 200:
            self.score_p += 50 * self.combo
            self.burst(self.bx, TOP_Y, JADE, 28)
            self.reset_rally(serve=1)
        elif self.by > 1760:
            self.score_a += 50
            self.combo = 1
            self.burst(self.bx, BOT_Y, MAG, 28)
            self.reset_rally(serve=-1)
        self.trail.append((self.bx, self.by))
        if len(self.trail) > 18:
            self.trail.pop(0)
        live = []
        for sp in self.sparks:
            sp.life -= dt
            if sp.life <= 0:
                continue
            sp.x += sp.vx * dt
            sp.y += sp.vy * dt
            live.append(sp)
        self.sparks = live
        for st in self.stars:
            st[1] += (6 + st[2] * 5) * dt
            if st[1] > 1700:
                st[1] = 230
                st[0] = random.uniform(0, W)

    def paddle(self, s, cx, cy, col) -> None:
        r = pygame.Rect(int(cx - PW * 0.5), int(cy - PH * 0.5), PW, PH)
        pygame.draw.rect(s, col, r, border_radius=14)
        pygame.draw.rect(s, PEARL, r, 3, border_radius=14)
        glow = pygame.Rect(r.x + 18, r.y + 8, r.w - 36, 8)
        pygame.draw.rect(s, PEARL, glow, border_radius=6)

    def draw(self, s: pygame.Surface) -> None:
        s.fill(VOID)
        pygame.draw.rect(s, PINE, (0, 0, W, 210))
        pygame.draw.rect(s, PINE, (0, 1740, W, 180))
        pygame.draw.rect(s, MOSS, (0, 0, MARGIN, H))
        pygame.draw.rect(s, MOSS, (W - MARGIN, 0, MARGIN, H))
        pygame.draw.rect(s, JADE, (MARGIN - 6, 210, 8, 1530))
        pygame.draw.rect(s, JADE, (W - MARGIN - 2, 210, 8, 1530))
        for i in range(12):
            y = 280 + i * 120
            pygame.draw.line(s, (12, 56, 48), (MARGIN + 20, y), (W - MARGIN - 20, y), 2)
        pygame.draw.line(s, JADE, (MARGIN + 10, H // 2), (W - MARGIN - 10, H // 2), 3)
        for x, y, r in self.stars:
            pygame.draw.circle(s, (20, 90, 70), (int(x), int(y)), max(1, int(r)))
        for o in self.orbs:
            wob = 6 * math.sin(o.phase)
            col = GOLD if o.kind == "boost" else AMBER
            pygame.draw.circle(s, col, (int(o.x), int(o.y + wob)), 22)
            pygame.draw.circle(s, PEARL, (int(o.x), int(o.y + wob)), 8)
            pygame.draw.circle(s, col, (int(o.x), int(o.y + wob)), 22, 2)
        for i, (tx, ty) in enumerate(self.trail):
            pygame.draw.circle(s, (40, 160, 120), (int(tx), int(ty)), max(2, i // 3))
        pygame.draw.circle(s, MINT, (int(self.bx), int(self.by)), BR + 4)
        pygame.draw.circle(s, PEARL, (int(self.bx), int(self.by)), BR - 4)
        pygame.draw.circle(s, JADE, (int(self.bx), int(self.by)), BR + 4, 2)
        self.paddle(s, self.ax, TOP_Y, MAG)
        self.paddle(s, self.px, BOT_Y, JADE)
        for sp in self.sparks:
            pygame.draw.circle(s, sp.col, (int(sp.x), int(sp.y)), max(1, int(sp.r * sp.life * 2.4)))
        if self.flash > 0:
            fl = pygame.Surface((W, H), pygame.SRCALPHA)
            fl.fill((80, 255, 180, int(60 * self.flash / 0.1)))
            s.blit(fl, (0, 0))
        title = self.font_lg.render(TITLE, True, MINT)
        s.blit(title, title.get_rect(center=(W // 2, 52)))
        handle = self.font_sm.render(HANDLE, True, GOLD)
        s.blit(handle, handle.get_rect(center=(W // 2, 102)))
        hud = self.font_md.render(f"YOU  {self.score_p}    AI  {self.score_a}    x{self.combo}", True, CYAN)
        s.blit(hud, hud.get_rect(center=(W // 2, 156)))
        hint = self.font_sm.render("A/D or arrows slide   R reset   x.com/ElbowOS", True, JADE)
        s.blit(hint, hint.get_rect(center=(W // 2, H - 36)))

    def play(self) -> None:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                else:
                    self.handle(ev)
            self.update(dt)
            self.draw(self.surf)
            screen.blit(self.surf, (0, 0))
            pygame.display.flip()

    def record_mp4(self, path: str) -> None:
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart", path,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        frames = FPS * 15
        for i in range(frames):
            self.update(1.0 / FPS)
            self.draw(self.surf)
            proc.stdin.write(pygame.image.tostring(self.surf, "RGB"))
            if i % 30 == 0:
                print(f"frame {i}/{frames}", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed: {rc}")
        print("wrote", path)


def main() -> None:
    record = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
    play = "--play" in sys.argv
    if record or not play:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    g = Game(record or not play)
    if record or not play:
        out = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/MALACHITE_RALLY_ElbowOS.mp4")
        g.record_mp4(out)
    else:
        g.play()
    pygame.quit()


if __name__ == "__main__":
    main()
