import asyncio
from functools import wraps
from typing import Any

import spotipy

from spotify_mcp.models import (
    DevicesResponse,
    Episode,
    PlaybackState,
    RecentlyPlayedResponse,
    SavedTracksResponse,
    SearchResponse,
    ShowEpisodesResponse,
    SimplifiedPlaylist,
    TopTracksResponse,
)


SPOTIFY_SCOPES = [
    "user-read-playback-state",    # current_playback(), devices()
    "user-modify-playback-state",  # start_playback(), add_to_queue(), volume(), transfer_playback()
    
    "user-library-read",           # current_user_saved_tracks(), current_user_saved_tracks_contains()
    "user-library-modify",         # current_user_saved_tracks_add(), current_user_saved_tracks_delete()
    
    "user-top-read",               # current_user_top_tracks()
    "user-read-recently-played",   # current_user_recently_played()
    
    "playlist-modify-public",      # Create/modify public playlists
    "playlist-modify-private",     # Create/modify private playlists
]


class AsyncSpotify:
    """Async wrapper around spotipy.Spotify with Pydantic models."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize async Spotify client.

        Args:
            *args: Positional arguments passed to spotipy.Spotify
            **kwargs: Keyword arguments passed to spotipy.Spotify
        """
        self._client = spotipy.Spotify(*args, **kwargs)

    async def current_playback(
        self,
        market: str | None = None,
        additional_types: str | None = None,
    ) -> PlaybackState | None:
        result = await asyncio.to_thread(
            self._client.current_playback,
            market=market,
            additional_types=additional_types,
        )
        return PlaybackState.model_validate(result) if result else None

    async def devices(self) -> DevicesResponse:
        """Get a list of user's available devices.

        Returns:
            Response containing available devices
        """
        result = await asyncio.to_thread(self._client.devices)
        return DevicesResponse.model_validate(result)

    async def start_playback(
        self,
        device_id: str | None = None,
        context_uri: str | None = None,
        uris: list[str] | None = None,
        offset: dict[str, int | str] | None = None,
        position_ms: int | None = None,
    ) -> None:
        """Start or resume user's playback.

        Args:
            device_id: Device target for playback
            context_uri: Spotify context URI to play (album, artist, playlist)
            uris: List of Spotify track URIs
            offset: Offset into context by index or track URI
            position_ms: Position in milliseconds to start playback
        """
        return await asyncio.to_thread(
            self._client.start_playback,
            device_id=device_id,
            context_uri=context_uri,
            uris=uris,
            offset=offset,
            position_ms=position_ms,
        )

    async def add_to_queue(
        self,
        uri: str,
        device_id: str | None = None,
    ) -> None:
        """Add a song to the end of user's queue.

        Args:
            uri: Song URI, ID, or URL
            device_id: Device ID (None targets active device)
        """
        return await asyncio.to_thread(
            self._client.add_to_queue,
            uri=uri,
            device_id=device_id,
        )

    async def volume(
        self,
        volume_percent: int,
        device_id: str | None = None,
    ) -> None:
        """Set playback volume.

        Args:
            volume_percent: Volume between 0 and 100
            device_id: Device target for playback
        """
        return await asyncio.to_thread(
            self._client.volume,
            volume_percent=volume_percent,
            device_id=device_id,
        )

    async def transfer_playback(
        self,
        device_id: str,
        force_play: bool = True,
    ) -> None:
        """Transfer playback to another device.

        Args:
            device_id: Transfer playback to this device
            force_play: Whether to start playing after transfer
        """
        return await asyncio.to_thread(
            self._client.transfer_playback,
            device_id=device_id,
            force_play=force_play,
        )

    async def search(
        self,
        q: str,
        limit: int = 10,
        offset: int = 0,
        type: str = "track",
        market: str | None = None,
    ) -> SearchResponse:
        """Search for an item.

        Args:
            q: Search query
            limit: Number of items to return (1-50)
            offset: Index of first item to return
            type: Item types to search (comma-separated: 'track,album,artist')
            market: ISO 3166-1 alpha-2 country code

        Returns:
            Search results
        """
        result = await asyncio.to_thread(
            self._client.search,
            q=q,
            limit=limit,
            offset=offset,
            type=type,
            market=market,
        )
        return SearchResponse.model_validate(result)

    async def current_user_top_tracks(
        self,
        limit: int = 20,
        offset: int = 0,
        time_range: str = "medium_term",
    ) -> TopTracksResponse:
        """Get current user's top tracks.

        Args:
            limit: Number of entities to return
            offset: Index of first entity to return
            time_range: Time frame ('short_term', 'medium_term', 'long_term')

        Returns:
            Top tracks response
        """
        result = await asyncio.to_thread(
            self._client.current_user_top_tracks,
            limit=limit,
            offset=offset,
            time_range=time_range,
        )
        return TopTracksResponse.model_validate(result)

    async def user_playlist_create(
        self,
        user: str,
        name: str,
        public: bool = True,
        collaborative: bool = False,
        description: str = "",
    ) -> SimplifiedPlaylist:
        """Create a playlist for a user.

        Args:
            user: User ID
            name: Playlist name
            public: Whether playlist is public
            collaborative: Whether playlist is collaborative
            description: Playlist description

        Returns:
            Created playlist
        """
        result = await asyncio.to_thread(
            self._client.user_playlist_create,
            user=user,
            name=name,
            public=public,
            collaborative=collaborative,
            description=description,
        )
        return SimplifiedPlaylist.model_validate(result)

    async def current_user_saved_tracks(
        self,
        limit: int = 20,
        offset: int = 0,
        market: str | None = None,
    ) -> SavedTracksResponse:
        """Get tracks saved in the current user's library.

        Args:
            limit: Number of tracks to return (max 50)
            offset: Index of first track to return
            market: ISO 3166-1 alpha-2 country code

        Returns:
            Saved tracks response
        """
        result = await asyncio.to_thread(
            self._client.current_user_saved_tracks,
            limit=limit,
            offset=offset,
            market=market,
        )
        return SavedTracksResponse.model_validate(result)

    async def current_user_saved_tracks_contains(
        self,
        tracks: list[str] | None = None,
    ) -> list[bool]:
        """Check if tracks are in user's library.

        Args:
            tracks: List of track URIs, URLs, or IDs

        Returns:
            List of booleans indicating saved status
        """
        return await asyncio.to_thread(
            self._client.current_user_saved_tracks_contains,
            tracks=tracks,
        )

    async def current_user_saved_tracks_add(
        self,
        tracks: list[str] | None = None,
    ) -> None:
        """Add tracks to user's library.

        Args:
            tracks: List of track URIs, URLs, or IDs
        """
        return await asyncio.to_thread(
            self._client.current_user_saved_tracks_add,
            tracks=tracks,
        )

    async def current_user_saved_tracks_delete(
        self,
        tracks: list[str] | None = None,
    ) -> None:
        """Remove tracks from user's library.

        Args:
            tracks: List of track URIs, URLs, or IDs
        """
        return await asyncio.to_thread(
            self._client.current_user_saved_tracks_delete,
            tracks=tracks,
        )

    async def current_user_recently_played(
        self,
        limit: int = 50,
        after: int | None = None,
        before: int | None = None,
    ) -> RecentlyPlayedResponse:
        """Get current user's recently played tracks.

        Args:
            limit: Number of entities to return
            after: Unix timestamp in ms (returns items after this)
            before: Unix timestamp in ms (returns items before this)

        Returns:
            Recently played tracks response
        """
        result = await asyncio.to_thread(
            self._client.current_user_recently_played,
            limit=limit,
            after=after,
            before=before,
        )
        return RecentlyPlayedResponse.model_validate(result)

    async def episode(
        self,
        episode_id: str,
        market: str | None = None,
    ) -> Episode:
        """Get a single episode.

        Args:
            episode_id: Episode ID, URI, or URL
            market: ISO 3166-1 alpha-2 country code

        Returns:
            Episode information
        """
        result = await asyncio.to_thread(
            self._client.episode,
            episode_id=episode_id,
            market=market,
        )
        return Episode.model_validate(result)

    async def show_episodes(
        self,
        show_id: str,
        limit: int = 50,
        offset: int = 0,
        market: str | None = None,
    ) -> ShowEpisodesResponse:
        """Get episodes from a show.

        Args:
            show_id: Show ID, URI, or URL
            limit: Number of items to return
            offset: Index of first item to return
            market: ISO 3166-1 alpha-2 country code

        Returns:
            Show episodes response
        """
        result = await asyncio.to_thread(
            self._client.show_episodes,
            show_id=show_id,
            limit=limit,
            offset=offset,
            market=market,
        )
        return ShowEpisodesResponse.model_validate(result)

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to wrapped client."""
        attr = getattr(self._client, name)

        if callable(attr):

            @wraps(attr)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await asyncio.to_thread(attr, *args, **kwargs)

            return async_wrapper

        return attr