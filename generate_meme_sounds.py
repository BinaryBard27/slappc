import wave
import struct
import math
import os
import random

def generate_wav(filename, frequency, duration=0.5, decay=False):
    """Generate a WAV file with optional decay."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        
        data = []
        for i in range(n_samples):
            if decay:
                # Exponential decay for impact sounds
                envelope = math.exp(-3 * i / n_samples)
            else:
                envelope = 1.0
            
            value = int(32767 * envelope * math.sin(2 * math.pi * frequency * i / sample_rate))
            data.append(value)
        
        w.writeframes(struct.pack('h' * len(data), *data))

def generate_noise_wav(filename, duration=0.3):
    """Generate white noise WAV."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        
        data = []
        for i in range(n_samples):
            envelope = math.exp(-5 * i / n_samples)
            value = int(32767 * envelope * (random.random() * 2 - 1))
            data.append(value)
        
        w.writeframes(struct.pack('h' * len(data), *data))

def generate_sweep_wav(filename, start_freq, end_freq, duration=0.5):
    """Generate frequency sweep."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        
        data = []
        for i in range(n_samples):
            t = i / sample_rate
            # Linear frequency sweep
            freq = start_freq + (end_freq - start_freq) * (i / n_samples)
            envelope = math.exp(-2 * i / n_samples)
            value = int(32767 * envelope * math.sin(2 * math.pi * freq * t))
            data.append(value)
        
        w.writeframes(struct.pack('h' * len(data), *data))

# Create meme pack
meme_dir = "sounds/pack_meme"
os.makedirs(meme_dir, exist_ok=True)

print("Generating meme sound pack...")

# Vine Boom - low frequency boom with decay
generate_wav(f"{meme_dir}/vine_boom.wav", 80, duration=0.4, decay=True)
print(f"Created {meme_dir}/vine_boom.wav")

# Bruh - descending tone
generate_sweep_wav(f"{meme_dir}/bruh.wav", 300, 100, duration=0.6)
print(f"Created {meme_dir}/bruh.wav")

# Windows XP Error - ascending chime
generate_sweep_wav(f"{meme_dir}/xp_error.wav", 400, 800, duration=0.3)
print(f"Created {meme_dir}/xp_error.wav")

# OOF - short impact
generate_wav(f"{meme_dir}/oof.wav", 200, duration=0.15, decay=True)
print(f"Created {meme_dir}/oof.wav")

# MLG Airhorn - noise burst
generate_noise_wav(f"{meme_dir}/airhorn.wav", duration=0.5)
print(f"Created {meme_dir}/airhorn.wav")

print("Meme sound pack complete!")
