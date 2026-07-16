import wave
import struct
import math
import os

def generate_wav(filename, frequency, duration=1.0):
    """Generate a simple sine wave WAV file."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        
        data = []
        for i in range(n_samples):
            value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            data.append(value)
        
        w.writeframes(struct.pack('h' * len(data), *data))

# Create scream pack
scream_dir = "sounds/pack_scream"
os.makedirs(scream_dir, exist_ok=True)

frequencies = [440, 880, 660, 550, 770]
for i, freq in enumerate(frequencies, 1):
    generate_wav(f"{scream_dir}/scream{i}.wav", freq)
    print(f"Created {scream_dir}/scream{i}.wav")

# Create goat pack
goat_dir = "sounds/pack_goat"
os.makedirs(goat_dir, exist_ok=True)

goat_freqs = [300, 400, 500, 600, 700]
for i, freq in enumerate(goat_freqs, 1):
    generate_wav(f"{goat_dir}/goat{i}.wav", freq)
    print(f"Created {goat_dir}/goat{i}.wav")

print("All sound files generated!")
