# Malachite Rally

Full-colour **Python 3** neon pong/volley arcade for ElbowOS.

Featured: [https://x.com/ElbowOS](https://x.com/ElbowOS)

Drive reel: [MALACHITE_RALLY_ElbowOS.mp4](https://drive.google.com/file/d/1ZEQJnHjvZ8VXL_26Htn2PUAnteUNHfoh/view?usp=drivesdk)

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 malachite_rally.py --play
```

- **A / D** or **← →** slide your jade paddle
- **R** reset
- **Esc** quit

Keep the ball in play. Gold orbs boost speed; amber orbs curve the shot. Combos multiply points.

## Record a 9:16 reel

```bash
python3 malachite_rally.py --record
```

Writes `/home/workdir/artifacts/MALACHITE_RALLY_ElbowOS.mp4` (1080×1920, 15s, 30fps, H.264).
Needs `ffmpeg` on PATH.

Requires Python 3.10+ and pygame. Dummy SDL is used when recording so a display is optional.
