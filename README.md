# ATS Engine Sound Prototype

A small procedural audio prototype for the engine concept in this repository: a rough, aggressive diesel idle with a prominent turbo spool. It uses only Python's standard library and writes three WAV clips you can audition and use as starting material in an audio workstation.

## Generate the clips

```bash
python3 tools/generate_engine.py
```

This creates `output/engine_start.wav`, `output/engine_idle.wav`, and `output/engine_rev.wav` as 48 kHz, 16-bit mono PCM. Adjust the settings near the top of the script to change the idle speed, duration, and turbo level.

## Important

These are synthesized sound-design sketches, not recordings of a real engine and not a drop-in American Truck Simulator mod. To make an in-game sound mod, the clips still need editing/mixing and integration into the appropriate SCS audio definitions and FMOD project for the target truck. The exact integration depends on the truck and game/mod setup.
