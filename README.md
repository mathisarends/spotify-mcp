# Spotify MCP Server

An async MCP (Model Context Protocol) server for Spotify playback control and search functionality.

## Features

- Async wrapper around Spotify API using Pydantic models
- Device name resolution with automatic caching
- Comprehensive playback control
- Track and album search
- Recently played history

## Setup

### Prerequisites

- Python 3.14+
- Spotify API credentials (Client ID, Secret, Redirect URI)

### Environment Variables

Create a `.env` file in the project root:

```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

OPENAI_API_KEY=your-openai-api-key # or other llm-provider
```

### Installation

```bash
uv run python -m spotify_mcp.server
```

## Available Tools

### Playback Control

- **get_current_playback** - Get current playback state and track info
- **start_playback** - Start playback (context_uri for albums/artists, uris for track lists)
- **pause_playback** - Pause current playback
- **next_track** - Skip to next track
- **previous_track** - Skip to previous track
- **set_shuffle** - Enable/disable shuffle mode

### Device Management

- **get_devices** - Get available devices (updates device resolver cache)
- **transfer_playback** - Transfer playback to another device
- **set_volume** - Set device volume (0-100)

### Queue Management

- **add_to_queue** - Add track to queue

### Search

- **search_tracks** - Search for tracks
- **search_albums** - Search for albums
- **play_album** - Play an album directly

### History

- **get_recently_played** - Get recently played tracks

## Usage Examples

### With MCP Server and Agent

```python
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv(override=True)


async def interactive_session():
    async with MCPServerStdio(
        name="Spotify Server",
        params={
            "command": "uv",
            "args": ["run", "spotify-mcp"],
        },
    ) as spotify_server:
        agent = Agent(
            name="Spotify DJ",
            instructions="""
            You are a professional DJ Assistant.
            - Play music based on mood and genre
            - Manage playlists intelligently
            - Adjust volume based on context
            """,
            mcp_servers=[spotify_server],
        )

        print("🎵 Spotify DJ started!")
        print("Type 'exit' to quit\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                break

            if not user_input:
                continue

            result = await Runner.run(agent, user_input)
            print(f"🤖 Assistant: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(interactive_session())
```

### Direct Client Usage

```python
import asyncio
from spotify_mcp import AsyncSpotify
from spotipy.oauth2 import SpotifyOAuth
import os

async def main():
    # Initialize client
    client = AsyncSpotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        )
    )

    playback = await client.current_playback()
    if playback and playback.item:
        print(f"Now playing: {playback.item.name}")

    results = await client.search(q="The Beatles", type="track", limit=5)
    for track in results.tracks.items:
        print(f"Track: {track.name} by {', '.join(a.name for a in track.artists)}")

    # Pause playback
    await client.pause_playback()

    # Skip to next track
    await client.next_track()


if __name__ == "__main__":
    asyncio.run(main())
```

## MCP Tool Usage

All tools accept `device_name` parameter to target specific devices. If not provided, the active device is used.

### Example with Claude/LLM:

```
User: Play the album "Abbey Road" on my bedroom speaker
→ search_albums("Abbey Road")
→ play_album(album_uri, device_name="bedroom speaker")

User: What's currently playing?
→ get_current_playback()
→ Returns: PlaybackState with current track info

User: Skip to the next track
→ next_track()
```

## Device Resolution

The server caches device names at startup. If you add new devices, use `get_devices` tool to refresh the cache.

Device names are case-insensitive and automatically resolved to device IDs.

## Architecture

- **client.py** - Async wrapper around Spotify API
- **device_resolver.py** - Device name → ID mapping cache
- **models.py** - Pydantic models for type safety
- **server.py** - FastMCP server with tool definitions
- **types.py** - Enums and response types

### Developer Resources

https://developer.spotify.com/dashboard
