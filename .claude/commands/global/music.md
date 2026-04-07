---
name: music
description: Download audio from YouTube/SoundCloud URL and upload to SonyJuke
---

Run the `music` command with the provided URL argument. The script at `~/bin/music` handles:
- Audio extraction via yt-dlp
- Conversion to MP3 via ffmpeg  
- Upload to Sony Z1C at 192.168.178.54:5000

Usage: `~/bin/music $ARGUMENTS`

If the URL is a playlist, add `--all` flag to download all tracks.
