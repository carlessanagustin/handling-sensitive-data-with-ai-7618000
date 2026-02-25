# Open WebUI with SearXNG and Edge-TTS

This setup includes:
- **Open WebUI**: Main AI chat interface (port 3000)
- **SearXNG**: Privacy-respecting search engine (port 4000)  
- **Edge-TTS**: Text-to-speech service (port 5000)

## Quick Start

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the services:**
   - Open WebUI: http://localhost:3000
   - SearXNG: http://localhost:4000  
   - Edge-TTS API: http://localhost:5000

## Service Details

### Open WebUI
- Main chat interface with AI models
- Integrated with SearXNG for web search capabilities
- Supports TTS through Edge-TTS service

### SearXNG
- Privacy-focused search engine
- Aggregates results from multiple sources
- No tracking or data collection
- Custom configuration in `searxng/settings.yml`

### Edge-TTS
- Microsoft Edge Text-to-Speech service
- High-quality neural voices
- RESTful API for integration
- Supports multiple languages and voices

## Configuration

### SearXNG Settings
Edit `searxng/settings.yml` to:
- Change search engines
- Modify UI theme
- Adjust safety settings
- Configure languages

### Edge-TTS Voices
Available voices can be listed at: http://localhost:5000/voices

Common voices:
- `en-US-AriaNeural` (default)
- `en-US-JennyNeural`
- `en-GB-SoniaNeural`
- `es-ES-ElviraNeural`
- `fr-FR-DeniseNeural`

### Environment Variables
Modify the docker-compose.yml to change:

```yaml
environment:
  - EDGE_TTS_VOICE=en-US-AriaNeural
  - EDGE_TTS_RATE=+0%
  - EDGE_TTS_VOLUME=+0%
```

## API Usage

### Edge-TTS API
Convert text to speech:
```bash
curl -X POST http://localhost:5000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test!"}' \
  --output test.mp3
```

Get available voices:
```bash
curl http://localhost:5000/voices
```

### SearXNG Search
Direct search (JSON):
```bash
curl "http://localhost:4000/search?q=artificial%20intelligence&format=json"
```

## Integration with Open WebUI

### Search Integration
Open WebUI is configured to use SearXNG with:
```
SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>
```

### TTS Integration
The Edge-TTS service can be integrated into Open WebUI by configuring the TTS endpoint in the Open WebUI settings to point to:
```
http://edge-tts:5000/tts
```

## Troubleshooting

### Check service status:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs openwebui
docker-compose logs searxng
docker-compose logs edge-tts
```

### Restart services:
```bash
docker-compose restart
```

### Clean restart:
```bash
docker-compose down
docker-compose up -d
```

## Data Persistence

All services use Docker volumes for data persistence:
- `open-webui`: Open WebUI data
- `searxng-data`: SearXNG configuration and cache
- `edge-tts-data`: Edge-TTS cache files

## Security Notes

1. Change the SearXNG secret key in `searxng/settings.yml`
2. Consider using reverse proxy for production deployment
3. Firewall rules may be needed for external access
4. Regular updates recommended for security patches

## Support

For issues:
- Open WebUI: https://github.com/open-webui/open-webui
- SearXNG: https://github.com/searxng/searxng  
- Edge-TTS: https://github.com/rany2/edge-tts
