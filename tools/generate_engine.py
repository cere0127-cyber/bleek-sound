#!/usr/bin/env python3
"""Generate rough diesel-engine sound-design sketches with Python's stdlib.

The output is intentionally a stylized prototype, not a realistic recording.
"""

import math
import os
import random
import wave
from array import array

SAMPLE_RATE = 48_000
IDLE_RPM = 720
TURBO_LEVEL = 0.42
OUTPUT_DIR = "output"


def clamp(value):
    return max(-1.0, min(1.0, value))


def write_wav(filename, samples):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pcm = array("h", (int(clamp(x) * 32767) for x in samples))
    with wave.open(filename, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())


def synth_clip(duration, rpm_at, throttle_at, seed=7):
    """Synthesize a loping six-cylinder diesel and turbo layer."""
    rng = random.Random(seed)
    count = int(duration * SAMPLE_RATE)
    samples = []
    crank_phase = 0.0
    turbo_phase = 0.0
    noise_state = 0.0

    for i in range(count):
        t = i / SAMPLE_RATE
        rpm = rpm_at(t)
        throttle = max(0.0, min(1.0, throttle_at(t)))
        firing_hz = max(1.0, rpm / 20.0)  # Four-stroke inline-six firing rate
        crank_phase += 2.0 * math.pi * firing_hz / SAMPLE_RATE
        turbo_hz = 420.0 + 1_850.0 * throttle
        turbo_phase += 2.0 * math.pi * turbo_hz / SAMPLE_RATE

        # A soft-edged, harmonic firing pulse gives the low diesel chug.
        pulse = 0.0
        for harmonic in range(1, 8):
            pulse += math.sin(crank_phase * harmonic) / harmonic
        pulse *= 0.12 + 0.07 * math.sin(2.0 * math.pi * 2.4 * t)

        # Low engine-body rumble and uneven combustion texture.
        rumble = 0.20 * math.sin(2.0 * math.pi * (36.0 + rpm * 0.035) * t)
        noise_state = 0.94 * noise_state + 0.06 * rng.uniform(-1.0, 1.0)
        texture = noise_state * (0.08 + 0.13 * throttle)

        # Turbo whistle rises with throttle, with a filtered-noise hiss layer.
        spool = max(0.0, min(1.0, (throttle - 0.08) / 0.7))
        whistle = math.sin(turbo_phase) * TURBO_LEVEL * spool
        hiss = rng.uniform(-1.0, 1.0) * 0.12 * spool
        samples.append((pulse + rumble + texture + whistle + hiss) * 0.72)

    return samples


def main():
    # Starter: a brief crank-up into the rough idle.
    start = synth_clip(
        3.2,
        lambda t: 150 + 570 * min(1.0, max(0.0, (t - 0.45) / 0.75)),
        lambda t: 0.18 if t < 0.55 else 0.12,
        seed=11,
    )
    # Steady loop candidate; trim/crossfade its ends in an audio editor if needed.
    idle = synth_clip(8.0, lambda _t: IDLE_RPM, lambda _t: 0.10, seed=12)
    # A throttle sweep with a conspicuous turbo rise and fall.
    rev = synth_clip(
        7.0,
        lambda t: 800 + 1_500 * min(1.0, max(0.0, (t - 0.7) / 3.4))
        if t < 4.1
        else 2_300 - 1_500 * min(1.0, (t - 4.1) / 2.2),
        lambda t: min(1.0, t / 1.4) if t < 4.0 else max(0.0, 1.0 - (t - 4.0) / 2.0),
        seed=13,
    )

    write_wav(os.path.join(OUTPUT_DIR, "engine_start.wav"), start)
    write_wav(os.path.join(OUTPUT_DIR, "engine_idle.wav"), idle)
    write_wav(os.path.join(OUTPUT_DIR, "engine_rev.wav"), rev)
    print(f"Wrote prototype WAV clips to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
