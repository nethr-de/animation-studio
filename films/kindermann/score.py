"""Original score for the Kindermann film: warm, unhurried, 96 BPM, 8 bars = exactly 20 s.

Felt piano, upright bass, brushes, plus quiet hits on the film's cuts. Everything is synthesized
here with seeded noise, so the file is identical on every run. Two cycles are rendered and the
second is kept, so reverb tails wrap and the loop is seamless.

    python3 films/kindermann/score.py   ->  out/kindermann/score.wav, films/kindermann/beats.json
"""
import json
import os

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'out', 'kindermann')
os.makedirs(OUT, exist_ok=True)

SR = 48000
BPM = 96
BEAT = 60 / BPM            # 0.625 s
BEATS = 32
DUR = BEATS * BEAT         # 20 s
rng = np.random.default_rng(20)  # seeded: no Math.random equivalent anywhere

N = int(DUR * SR)
mix = np.zeros((2, 2 * N))   # two cycles


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def add(sig, t, pan=0.0, gain=1.0):
    """Place a mono signal at time t (seconds) in both cycles, constant-power pan."""
    l = np.cos((pan + 1) * np.pi / 4) * gain
    r = np.sin((pan + 1) * np.pi / 4) * gain
    for cyc in (0, 1):
        i = int(round((t + cyc * DUR) * SR))
        j = min(i + len(sig), 2 * N)
        if i >= 2 * N:
            continue
        mix[0, i:j] += sig[: j - i] * l
        mix[1, i:j] += sig[: j - i] * r


def felt_piano(midi, dur=2.4, vel=0.5):
    f = hz(midi)
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # slightly stretched partials, upper ones die fast: a soft felt hammer
    for k, a in enumerate([1.0, 0.42, 0.18, 0.08, 0.035], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        out += a * np.sin(2 * np.pi * fk * t + k) * np.exp(-t * (1.1 + 1.6 * k) * (f / 400) ** 0.3)
    out += 0.25 * np.sin(2 * np.pi * f * 1.002 * t) * np.exp(-t * 1.4)   # gentle beating
    att = np.minimum(1, t / 0.012)
    rel = np.where(t > dur, np.exp(-(t - dur) * 6), 1)
    return out * att * rel * vel


def bass(midi, dur=0.55, vel=0.6):
    f = hz(midi)
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.006) * np.exp(-t * 3.2)
    env *= np.where(t > dur, np.exp(-(t - dur) * 14), 1)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8)
    return np.tanh(1.4 * s) * env * vel


def brush(dur=0.18, vel=0.12, bright=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    # crude band-pass: difference of two one-pole lowpasses
    def lp(x, a):
        y = np.zeros_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc += a * (x[i] - acc)
            y[i] = acc
        return y
    s = lp(noise, 0.35 + 0.3 * bright) - lp(noise, 0.06)
    return s * np.exp(-t * 26) * np.minimum(1, t / 0.004) * vel


def knock(freq=180, vel=0.5):
    """Soft wooden knock: a damped sine with a quick pitch drop, for cuts."""
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 18) * np.minimum(1, t / 0.002) * vel


def pluck(midi, vel=0.25):
    """Small bright pluck for the red dots and menu prices (a marimba-like bar)."""
    f = hz(midi)
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.3 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t * 30)
    return s * np.minimum(1, t / 0.002) * vel


def swish(dur=0.45, vel=0.08):
    """Paper-like swish for the two page scrolls."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n)
    s = np.convolve(s, np.ones(24) / 24, mode='same')
    env = np.sin(np.pi * np.minimum(1, t / dur)) ** 2
    return s * env * vel


# --- harmony: F major, one chord per bar (2.5 s) ---
F, A, Bb, C, D, E, G = 65, 69, 70, 72, 74, 76, 67
chords = [
    [53, 60, 64, 69, 72],   # bar 1  Fmaj7 (hook)
    [57, 60, 64, 67, 72],   # bar 2  Am7   (food)
    [58, 62, 65, 69, 72],   # bar 3  Bbmaj7 (food -> occasions)
    [55, 62, 65, 67, 70],   # bar 4  Gm7   (occasions)
    [50, 57, 60, 65, 69],   # bar 5  Dm7   (menu)
    [58, 62, 65, 69, 74],   # bar 6  Bbmaj7/add
    [55, 60, 65, 67, 70],   # bar 7  C7sus4 (Sie feiern)
    [53, 60, 64, 65, 69],   # bar 8  Fadd9  (logo, resolves, loops back)
]
roots = [41, 45, 46, 43, 38, 46, 48, 41]
fifths = [48, 52, 53, 50, 45, 53, 55, 48]

for bar, ch in enumerate(chords):
    t0 = bar * 4 * BEAT
    # chord on 1, rolled like a hand on the keys, then a softer re-voice on beat 3
    for i, m in enumerate(ch):
        add(felt_piano(m, dur=2.3, vel=0.26), t0 + i * 0.018, pan=-0.25 + 0.12 * i)
    for i, m in enumerate(ch[1:4]):
        add(felt_piano(m, dur=1.0, vel=0.12), t0 + 2 * BEAT + 0.5 * BEAT + i * 0.012, pan=0.2)
    # upright bass: root on 1, fifth on 3, a pickup on 4+ toward the next bar
    add(bass(roots[bar], 0.9), t0, gain=1.0)
    add(bass(fifths[bar], 0.5, 0.45), t0 + 2 * BEAT, gain=1.0)
    nxt = roots[(bar + 1) % 8]
    add(bass(nxt + 2 if nxt + 2 != roots[bar] else nxt - 1, 0.25, 0.3), t0 + 3.5 * BEAT)
    # brushes: soft eighths, accent on 2 and 4
    for e in range(8):
        acc = 1.6 if e in (2, 6) else 1.0
        add(brush(vel=0.05 * acc, bright=0.4 if e % 2 else 0.7), t0 + e * BEAT / 2 + (0.012 if e % 2 else 0), pan=0.35)

# --- melody: a short, unhurried phrase in the right hand ---
melody = [  # (beat, midi, length in beats)
    (1, 72, 1), (2, 74, 1), (3, 77, 2),          # Gutes. Essen. Hausgemacht.
    (6, 76, 1), (7, 74, 0.5), (8, 72, 1.5),
    (11, 74, 2), (13, 72, 2), (15, 70, 2),        # Hochzeit, Private Feier, Firmenfeier
    (18, 69, 1), (19, 72, 1), (20, 77, 2),       # menu lines
    (23, 76, 2), (25.5, 74, 0.5), (26, 72, 1), (27, 77, 2),
    (29, 76, 1.5), (30.5, 72, 1.5),
]
for b, m, ln in melody:
    add(felt_piano(m + 12, dur=ln * BEAT * 0.95, vel=0.2), b * BEAT, pan=0.15)

# --- hits on the cuts (the film's beat grid) ---
for b in (1, 2, 3):
    add(knock(150, 0.45), b * BEAT)
for b, m in ((1.5, 89), (2.5, 91), (3.5, 96)):        # red dots
    add(pluck(m, 0.12), b * BEAT, pan=0.3)
for b in (5, 23):                                      # page scrolls
    add(swish(0.4, 0.07), b * BEAT - 0.05, pan=-0.2)
for b in (7, 8, 9, 11, 17):                            # cuts
    add(knock(210, 0.3), b * BEAT, pan=-0.1)
for b in (13, 15):                                     # prints landing
    add(knock(170, 0.3), b * BEAT + 0.06)
for b, m in ((18.5, 84), (19.5, 86), (20.5, 89)):      # prices
    add(pluck(m, 0.13), b * BEAT, pan=0.25)
add(swish(0.35, 0.06), 25.5 * BEAT - 0.05, pan=0.2)    # red rises
add(knock(130, 0.35), 29 * BEAT)                       # logo

# --- room: short synthetic reverb (seeded noise IR) ---
ir_len = int(1.6 * SR)
ti = np.arange(ir_len) / SR
for c in range(2):
    ir = rng.standard_normal(ir_len) * np.exp(-ti * 3.6)
    ir[:int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = np.fft.irfft(np.fft.rfft(mix[c], 2 * N + ir_len) * np.fft.rfft(ir, 2 * N + ir_len))[: 2 * N]
    mix[c] = mix[c] + 0.22 * wet

# keep the second cycle: tails from the end have wrapped into its start
out = mix[:, N:2 * N].T.copy()
out = np.tanh(out * 1.2) / 1.2

meter = pyln.Meter(SR)
gain = pyln.normalize.loudness(out, meter.integrated_loudness(out), -14.0)
peak = np.max(np.abs(gain))
if peak > 0.89:  # about -1 dBFS: gentle soft-knee limiting instead of clipping
    gain = np.sign(gain) * np.where(np.abs(gain) > 0.7, 0.7 + 0.19 * np.tanh((np.abs(gain) - 0.7) / 0.19), np.abs(gain))
    gain = pyln.normalize.loudness(gain, meter.integrated_loudness(gain), -14.0)
lufs = meter.integrated_loudness(gain)
sf.write(os.path.join(OUT, 'score.wav'), gain, SR, subtype='PCM_24')

# --- measure the beat grid from the audio and fit it ---
y = librosa.to_mono(gain.T)
tempo, frames = librosa.beat.beat_track(y=y, sr=SR, start_bpm=BPM, units='time', tightness=400)
meas = np.asarray(frames)
idx = np.round(meas / BEAT)
A_ = np.vstack([idx, np.ones_like(idx)]).T
period, phase = np.linalg.lstsq(A_, meas, rcond=None)[0]
grid = [round(float(phase + period * k), 4) for k in range(BEATS + 1)]
# the loop has to close on exactly 20 s. If the measured grid agrees with the written one to
# within one frame at 24 fps (librosa's onset envelope lags the attack by ~1 hop), cuts cannot be
# placed any closer, so use the written grid; otherwise keep the measurement
drift = max(abs(g - k * BEAT) for k, g in enumerate(grid))
beats = [round(k * BEAT, 4) for k in range(BEATS + 1)] if drift < 1 / 24 else grid
json.dump({
    'bpm': BPM, 'measured_bpm': round(60 / period, 3), 'measured_phase_s': round(float(phase), 4),
    'max_drift_s': round(drift, 4), 'n_measured_beats': int(len(meas)), 'lufs': round(lufs, 2),
    'beats': beats,
}, open(os.path.join(HERE, 'beats.json'), 'w'), indent=1)
print(f'score.wav  {lufs:.2f} LUFS  peak {20*np.log10(np.max(np.abs(gain))):.2f} dBFS  '
      f'measured {60/period:.2f} BPM phase {phase*1000:.1f} ms  drift {drift*1000:.1f} ms')
