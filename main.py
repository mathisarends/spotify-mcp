import os
from spotipy.oauth2 import SpotifyOAuth
from spotify_mcp import AsyncSpotify, SpotifyScope
from dotenv import load_dotenv

load_dotenv(override=True)

_SPOTIFY_SCOPES = [
    SpotifyScope.USER_READ_PLAYBACK_STATE,     # current_playback(), devices()
    SpotifyScope.USER_MODIFY_PLAYBACK_STATE,   # start_playback(), add_to_queue(), volume(), transfer_playback()
    SpotifyScope.USER_LIBRARY_READ,            # current_user_saved_tracks(), current_user_saved_tracks_contains()
    SpotifyScope.USER_LIBRARY_MODIFY,          # current_user_saved_tracks_add(), current_user_saved_tracks_delete()
    SpotifyScope.USER_TOP_READ,                # current_user_top_tracks()
    SpotifyScope.USER_READ_RECENTLY_PLAYED,    # current_user_recently_played()
    SpotifyScope.PLAYLIST_MODIFY_PUBLIC,       # Create/modify public playlists
    SpotifyScope.PLAYLIST_MODIFY_PRIVATE,      # Create/modify private playlists
]


async def main():
    sp = AsyncSpotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=" ".join(_SPOTIFY_SCOPES),
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