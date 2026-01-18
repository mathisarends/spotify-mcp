import os
from spotipy.oauth2 import SpotifyOAuth
from spotify_mcp import AsyncSpotify
from dotenv import load_dotenv

load_dotenv(override=True)


_SPOTIFY_SCOPES = [
    "user-read-playback-state",    # current_playback(), devices()
    "user-modify-playback-state",  # start_playback(), add_to_queue(), volume(), transfer_playback()
    
    "user-library-read",           # current_user_saved_tracks(), current_user_saved_tracks_contains()
    "user-library-modify",         # current_user_saved_tracks_add(), current_user_saved_tracks_delete()
    
    "user-top-read",               # current_user_top_tracks()
    "user-read-recently-played",   # current_user_recently_played()
    
    "playlist-modify-public",      # Create/modify public playlists
    "playlist-modify-private",     # Create/modify private playlists
]


async def main():
    sp = AsyncSpotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=" ".join(_SPOTIFY_SCOPES),
            cache_path=".spotify_cache",
        )
    )

    devices = await sp.devices()
    for device in devices.devices:
        print(f"{device.name} – {device.id}")
        print(f"  Type: {device.type}, Active: {device.is_active}, Volume: {device.volume_percent}%")

    top_tracks = await sp.current_user_top_tracks(limit=10)
    for idx, track in enumerate(top_tracks.items, 1):
        artist_names = ", ".join(artist.name for artist in track.artists)
        print(f"{idx}. {artist_names} – {track.name}")
        print(f"   Album: {track.album.name if track.album else 'N/A'}")

    # Saved Tracks
    saved = await sp.current_user_saved_tracks(limit=5)
    print(f"\n📚 Total saved tracks: {saved.total}")
    for item in saved.items:
        print(f"Added {item.added_at}: {item.track.name}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())