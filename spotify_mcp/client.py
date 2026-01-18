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
        return await asyncio.to_thread(
            self._client.transfer_playback,
            device_id=device_id,
            force_play=force_play,
        )

    async def pause_playback(
        self,
        device_id: str | None = None,
    ) -> None:
        return await asyncio.to_thread(
            self._client.pause_playback,
            device_id=device_id,
        )

    async def search(
        self,
        q: str,
        limit: int = 10,
        offset: int = 0,
        type: str = "track",
        market: str | None = None,
    ) -> SearchResponse:
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
        return await asyncio.to_thread(
            self._client.current_user_saved_tracks_contains,
            tracks=tracks,
        )

    async def current_user_saved_tracks_add(
        self,
        tracks: list[str] | None = None,
    ) -> None:
        return await asyncio.to_thread(
            self._client.current_user_saved_tracks_add,
            tracks=tracks,
        )

    async def current_user_saved_tracks_delete(
        self,
        tracks: list[str] | None = None,
    ) -> None:
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