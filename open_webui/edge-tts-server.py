#!/usr/bin/env python3
"""
Edge-TTS Server for Open WebUI
Provides text-to-speech functionality using Microsoft Edge TTS
"""

import asyncio
import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import edge_tts
import uuid

app = Flask(__name__)
CORS(app)

# Configuration from environment variables
VOICE = os.environ.get('EDGE_TTS_VOICE', 'en-US-AriaNeural')
RATE = os.environ.get('EDGE_TTS_RATE', '+0%')
VOLUME = os.environ.get('EDGE_TTS_VOLUME', '+0%')
CACHE_DIR = '/app/cache'

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'edge-tts'})

@app.route('/voices', methods=['GET'])
def get_voices():
    """Get available voices"""
    async def _get_voices():
        voices = await edge_tts.list_voices()
        return [{'name': voice['Name'], 'display_name': voice['DisplayName'], 
                'locale': voice['Locale'], 'gender': voice['Gender']} for voice in voices]
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        voices = loop.run_until_complete(_get_voices())
        return jsonify({'voices': voices})
    finally:
        loop.close()

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', VOICE)
        rate = data.get('rate', RATE)
        volume = data.get('volume', VOLUME)
        
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Generate unique filename
        audio_id = str(uuid.uuid4())
        audio_file = os.path.join(CACHE_DIR, f"{audio_id}.mp3")
        
        # Convert text to speech
        async def _convert():
            communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
            await communicate.save(audio_file)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_convert())
        finally:
            loop.close()
        
        # Return the audio file
        return send_file(audio_file, mimetype='audio/mpeg', as_attachment=True, 
                        download_name=f'tts_{audio_id}.mp3')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts/stream', methods=['POST'])
def text_to_speech_stream():
    """Convert text to speech and return streaming URL"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', VOICE)
        rate = data.get('rate', RATE)
        volume = data.get('volume', VOLUME)
        
        # Generate unique filename
        audio_id = str(uuid.uuid4())
        audio_file = os.path.join(CACHE_DIR, f"{audio_id}.mp3")
        
        # Convert text to speech
        async def _convert():
            communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
            await communicate.save(audio_file)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_convert())
        finally:
            loop.close()
        
        # Return the URL to the audio file
        return jsonify({
            'audio_url': f'/audio/{audio_id}',
            'audio_id': audio_id,
            'voice': voice,
            'rate': rate,
            'volume': volume
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<audio_id>', methods=['GET'])
def get_audio(audio_id):
    """Serve audio file"""
    audio_file = os.path.join(CACHE_DIR, f"{audio_id}.mp3")
    if os.path.exists(audio_file):
        return send_file(audio_file, mimetype='audio/mpeg')
    else:
        return jsonify({'error': 'Audio file not found'}), 404

@app.route('/', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        'service': 'Edge-TTS Server',
        'version': '1.0.0',
        'endpoints': {
            '/health': 'Health check',
            '/voices': 'Get available voices',
            '/tts': 'Convert text to speech (direct file)',
            '/tts/stream': 'Convert text to speech (streaming URL)',
            '/audio/<id>': 'Get audio file by ID'
        },
        'current_voice': VOICE,
        'current_rate': RATE,
        'current_volume': VOLUME
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
