"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
from google.cloud.texttospeech import enums

def list_voices():
    """Lists the available voices."""
    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    for voice in voices.voices:
        # Display the voice's name. Example: tpc-vocoded
        print('Name: {}'.format(voice.name))

        # Display the supported language codes for this voice. Example: "en-US"
        for language_code in voice.language_codes:
            print('Supported language: {}'.format(language_code))

        ssml_gender = enums.SsmlVoiceGender(voice.ssml_gender)

        # Display the SSML Voice Gender
        print('SSML Voice Gender: {}'.format(ssml_gender.name))

        # Display the natural sample rate hertz for this voice. Example: 24000
        print('Natural Sample Rate Hertz: {}\n'.format(
            voice.natural_sample_rate_hertz))

def generate_speech(output_path, text="Hello!", speaking_rate=1.0, pitch=1.0):

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        name='en-US-Wavenet-F',
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE
        )

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate,
        pitch=pitch)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open(output_path, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file {}'.format(output_path))


