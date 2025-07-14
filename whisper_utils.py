import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import argparse
import os

def record_audio(duration=5, fs=16000):
    try:
        print(f"[🎙️] Recording for {duration} seconds...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        print("[✅] Recording complete.")
        return audio.flatten(), fs
    except Exception as e:
        print("[❌] Error recording audio:", e)
        return None, None

def save_wav(audio, fs):
    try:
        temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(temp.name, fs, audio)
        print(f"[💾] Saved audio to: {temp.name}")
        return temp.name
    except Exception as e:
        print("[❌] Failed to save audio:", e)
        return None

def transcribe_audio_whisper(audio_path, model_size="base"):
    try:
        print(f"[🧠] Loading Whisper model '{model_size}'...")
        model = whisper.load_model(model_size)
        print(f"[🔍] Transcribing...")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print("[❌] Transcription error:", e)
        return ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record and transcribe audio using Whisper")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration in seconds")
    parser.add_argument("--model", type=str, default="base", help="Whisper model size: tiny, base, small, medium, large")
    args = parser.parse_args()

    audio, fs = record_audio(duration=args.duration, fs=16000)
    if audio is not None and fs is not None:
        audio_path = save_wav(audio, fs)
        if audio_path:
            transcript = transcribe_audio_whisper(audio_path, model_size=args.model)
            print("\n[📝] Transcription:\n", transcript)
            os.remove(audio_path)  # Clean up temp file
