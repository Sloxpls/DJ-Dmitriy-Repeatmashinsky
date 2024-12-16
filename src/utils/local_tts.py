from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from IPython.display import Audio


class LocalTTS:
    def __init__(self):
        preload_models()

    def run(self, text, file_name):
        audio_array = generate_audio(text)
        write_wav(f"{file_name}", SAMPLE_RATE, audio_array)
        Audio(audio_array, rate=SAMPLE_RATE)
        return file_name
