from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.device_control import DeviceControlService
import io
import logging

logger = logging.getLogger(__name__)

audio_bp = Blueprint('audio', __name__)
device_service = DeviceControlService()


@audio_bp.route('/speak', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech audio.
    Returns an audio file (MP3/WAV).
    """
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'error': 'Text is required',
            'audio_message': 'No text to speak.'
        }), 400

    text = data['text']
    language = data.get('language', 'en')
    speed = data.get('speed', 1.0)

    try:
        # Try gTTS (Google Text-to-Speech) — works without API key
        from gtts import gTTS
        tts = gTTS(text=text, lang=language, slow=(speed < 0.8))
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )

    except ImportError:
        logger.warning("gTTS not installed, returning text-only response")
        return jsonify({
            'text': text,
            'audio_available': False,
            'audio_message': text,
            'note': 'Install gTTS for audio output: pip install gtts'
        }), 200

    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return jsonify({
            'text': text,
            'audio_available': False,
            'error': str(e)
        }), 500


@audio_bp.route('/process-voice', methods=['POST'])
@jwt_required()
def process_voice_command():
    """
    Process a voice command (text after speech-to-text).
    """
    data = request.get_json()

    if not data or 'command' not in data:
        return jsonify({
            'error': 'Command text required',
            'audio_message': 'I did not hear a command. Please try again.'
        }), 400

    command = data['command']

    result = device_service.process_voice_command(command)

    return jsonify(result), 200


@audio_bp.route('/transcribe', methods=['POST'])
@jwt_required()
def transcribe_audio():
    """
    Transcribe audio to text (Speech-to-Text).
    Accepts audio file upload.
    """
    if 'audio' not in request.files:
        return jsonify({
            'error': 'No audio file provided',
            'audio_message': 'Please send an audio recording.'
        }), 400

    audio_file = request.files['audio']
    audio_data = audio_file.read()

    try:
        # Try OpenAI Whisper
        import openai
        import os

        api_key = os.environ.get('OPENAI_API_KEY', '')
        if api_key:
            client = openai.OpenAI(api_key=api_key)

            # Save temporarily
            temp_path = '/tmp/lumi_audio_temp.wav'
            with open(temp_path, 'wb') as f:
                f.write(audio_data)

            with open(temp_path, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="en"
                )

            return jsonify({
                'text': transcript.text,
                'audio_message': f'I heard: {transcript.text}'
            }), 200

    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Transcription failed: {e}")

    # Fallback: try SpeechRecognition library
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        audio_buffer = io.BytesIO(audio_data)

        with sr.AudioFile(audio_buffer) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

            return jsonify({
                'text': text,
                'audio_message': f'I heard: {text}'
            }), 200

    except Exception as e:
        logger.error(f"Speech recognition failed: {e}")
        return jsonify({
            'error': 'Could not transcribe audio',
            'audio_message': 'Sorry, I could not understand the audio. Please speak clearly and try again.'
        }), 500


@audio_bp.route('/commands', methods=['GET'])
@jwt_required()
def get_commands():
    """Get list of available voice commands."""
    result = device_service.get_available_commands()
    return jsonify(result), 200