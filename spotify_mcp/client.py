import asyncio
from functools import wraps
from typing import Any

import spotipy

from spotify_mcp.models import (
    DevicesResponse,
    PlaybackState,
    RecentlyPlayedResponse,
    SearchResponse,
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

    async def next_track(
        self,
        device_id: str | None = None,
    ) -> None:
        return await asyncio.to_thread(
            self._client.next_track,
            device_id=device_id,
        )

    async def previous_track(
        self,
        device_id: str | None = None,
    ) -> None:
        return await asyncio.to_thread(
            self._client.previous_track,
            device_id=device_id,
        )

    async def shuffle(
        self,
        state: bool,
        device_id: str | None = None,
    ) -> None:
        return await asyncio.to_thread(
            self._client.shuffle,
            state=state,
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

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to wrapped client."""
        attr = getattr(self._client, name)

        if callable(attr):

            @wraps(attr)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await asyncio.to_thread(attr, *args, **kwargs)

            return async_wrapper

        return attr