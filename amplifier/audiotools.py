from pydub import AudioSegment
import logging

def mix_audio(background, voice, output_path, beginning_pad_seconds=1, end_pad_seconds=2):

    background_sound = AudioSegment.from_file(background)
    voice_sound = AudioSegment.from_file(voice)
    voice_len = voice_sound.duration_seconds

    total_len_seconds = beginning_pad_seconds + end_pad_seconds + voice_len

    background_sound_truncated = background_sound[:(total_len_seconds * 1000)]

    voice_padded = AudioSegment.silent(duration=beginning_pad_seconds * 1000) + voice_sound

    combined = background_sound_truncated.overlay(voice_padded)

    print(combined.duration_seconds)

    faded = combined.fade_out(duration=end_pad_seconds * 1000)

    print(faded.duration_seconds)

    faded.export(output_path, format='mp3')
