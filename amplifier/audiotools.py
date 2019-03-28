from pydub import AudioSegment
import logging

def mix_audio(path1, path2, output_path):

    sound1 = AudioSegment.from_mp3(path1)
    sound2 = AudioSegment.from_mp3(path2)

    combined = sound1.overlay(sound2)
    combined.export(output_path, format='mp3')
