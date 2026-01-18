from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from spotipy.oauth2 import SpotifyOAuth

from spotify_mcp import AsyncSpotify, SpotifyScope
from spotify_mcp.device_resolver import DeviceResolver
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
from spotify_mcp.types import ActionSuccessResponse

load_dotenv(override=True)

_SPOTIFY_SCOPES = [
    SpotifyScope.USER_READ_PLAYBACK_STATE,
    SpotifyScope.USER_MODIFY_PLAYBACK_STATE,
    SpotifyScope.USER_LIBRARY_READ,
    SpotifyScope.USER_LIBRARY_MODIFY,
    SpotifyScope.USER_TOP_READ,
    SpotifyScope.USER_READ_RECENTLY_PLAYED,
    SpotifyScope.PLAYLIST_MODIFY_PUBLIC,
    SpotifyScope.PLAYLIST_MODIFY_PRIVATE,
]


_spotify_client: AsyncSpotify | None = None
_device_resolver: DeviceResolver | None = None


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    global _spotify_client, _device_resolver

    _spotify_client = AsyncSpotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=" ".join(_SPOTIFY_SCOPES),
        )
    )

    _device_resolver = DeviceResolver()
    devices = await _spotify_client.devices()
    for device in devices.devices:
        _device_resolver.set_device(device.name, device.id)

    yield

    if _device_resolver:
        _device_resolver.invalidate()
    _device_resolver = None
    _spotify_client = None


mcp = FastMCP("Spotify MCP Server", lifespan=lifespan)

@mcp.tool()
async def get_current_playback(market: str | None = None) -> PlaybackState | None:
    return await _spotify_client.current_playback(market=market)


@mcp.tool()
async def get_devices() -> DevicesResponse:
    return await _spotify_client.devices()


@mcp.tool()
async def start_playback(
    device_name: str | None = None,
    context_uri: str | None = None,
    uris: list[str] | None = None,
    position_ms: int | None = None,
) -> ActionSuccessResponse:
    device_id = _device_resolver.resolve(device_name)
    await _spotify_client.start_playback(
        device_id=device_id,
        context_uri=context_uri,
        uris=uris,
        position_ms=position_ms,
    )
    return ActionSuccessResponse(message="Playback started")


@mcp.tool()
async def pause_playback(device_name: str | None = None) -> ActionSuccessResponse:
    device_id = _device_resolver.resolve(device_name)
    await _spotify_client.pause_playback(device_id=device_id)
    return ActionSuccessResponse(message="Playback paused")


@mcp.tool()
async def add_to_queue(uri: str, device_name: str | None = None) -> ActionSuccessResponse:
    device_id = _device_resolver.resolve(device_name)
    await _spotify_client.add_to_queue(uri=uri, device_id=device_id)
    return ActionSuccessResponse(message=f"Added {uri} to queue")


@mcp.tool()
async def set_volume(volume_percent: int, device_name: str | None = None) -> ActionSuccessResponse:
    device_id = _device_resolver.resolve(device_name)
    await _spotify_client.volume(volume_percent=volume_percent, device_id=device_id)
    return ActionSuccessResponse(message=f"Volume set to {volume_percent}%")


@mcp.tool()
async def transfer_playback(device_name: str, force_play: bool = True) -> ActionSuccessResponse:
    device_id = _device_resolver.resolve(device_name)
    if not device_id:
        return ActionSuccessResponse(message=f"Device '{device_name}' not found")
    await _spotify_client.transfer_playback(device_id=device_id, force_play=force_play)
    return ActionSuccessResponse(message=f"Playback transferred to device {device_name}")


@mcp.tool()
async def search_spotify(
    query: str,
    type: str = "track",
    limit: int = 10,
    market: str | None = None,
) -> SearchResponse:
    return await _spotify_client.search(q=query, type=type, limit=limit, market=market)


@mcp.tool()
async def get_saved_tracks(
    limit: int = 20,
    offset: int = 0,
    market: str | None = None,
) -> SavedTracksResponse:
    return await _spotify_client.current_user_saved_tracks(limit=limit, offset=offset, market=market)

# brauche ich nicht diese methode
@mcp.tool()
async def check_saved_tracks(track_ids: list[str]):
    result = await _spotify_client.current_user_saved_tracks_contains(tracks=track_ids)
    return {"tracks": track_ids, "saved": result}

# hier auch logishcen lookup für die tracks machen (cachen)
@mcp.tool()
async def save_tracks(track_ids: list[str]) -> ActionSuccessResponse:
    await _spotify_client.current_user_saved_tracks_add(tracks=track_ids)
    return ActionSuccessResponse(message=f"Saved {len(track_ids)} track(s)")


@mcp.tool()
async def remove_saved_tracks(track_ids: list[str]) -> ActionSuccessResponse:
    await _spotify_client.current_user_saved_tracks_delete(tracks=track_ids)
    return ActionSuccessResponse(message=f"Removed {len(track_ids)} track(s)")


@mcp.tool()
async def get_top_tracks(
    limit: int = 20,
    offset: int = 0,
    time_range: str = "medium_term",
) -> TopTracksResponse:
    return await _spotify_client.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)


@mcp.tool()
async def get_recently_played(
    limit: int = 20,
    after: int | None = None,
    before: int | None = None,
) -> RecentlyPlayedResponse:
    return await _spotify_client.current_user_recently_played(limit=limit, after=after, before=before)


@mcp.tool()
async def create_playlist(
    user_id: str,
    name: str,
    description: str = "",
    public: bool = True,
    collaborative: bool = False,
) -> SimplifiedPlaylist:
    return await _spotify_client.user_playlist_create(
        user=user_id,
        name=name,
        description=description,
        public=public,
        collaborative=collaborative,
    )


@mcp.tool()
async def get_episode(episode_id: str, market: str | None = None) -> Episode:
    return await _spotify_client.episode(episode_id=episode_id, market=market)


@mcp.tool()
async def get_show_episodes(
    show_id: str,
    limit: int = 20,
    offset: int = 0,
    market: str | None = None,
) -> ShowEpisodesResponse:
    return await _spotify_client.show_episodes(
        show_id=show_id,
        limit=limit,
        offset=offset,
        market=market,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio") 