from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from spotipy.oauth2 import SpotifyOAuth

from spotify_mcp import AsyncSpotify, SpotifyScope
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

load_dotenv()

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


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[None]:
    """ cache = get_cache() """ # hier könnte man einen lookup cache implementierne und den client in allen routen verfügbar machen
    # beziehungsweise auch nur instanziieren (für mehr geschwindigkeit der agents)

    # was ich machen möchte ist einen lookup nach namen und nciht nach device id 
    """ await cache.populate() """

    yield

    """ await cache.clear_all() """



mcp = FastMCP("Spotify MCP Server")

def get_spotify_client() -> AsyncSpotify:
    return AsyncSpotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=" ".join(_SPOTIFY_SCOPES),
        )
    )


@mcp.tool()
async def get_current_playback(market: str | None = None) -> PlaybackState | None:
    spotify_client = get_spotify_client()
    return await spotify_client.current_playback(market=market)


@mcp.tool()
async def get_devices() -> DevicesResponse:
    spotify_client = get_spotify_client()
    return await spotify_client.devices()


@mcp.tool()
async def start_playback(
    device_id: str | None = None,
    context_uri: str | None = None,
    uris: list[str] | None = None,
    position_ms: int | None = None,
) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.start_playback(
        device_id=device_id,
        context_uri=context_uri,
        uris=uris,
        position_ms=position_ms,
    )
    return ActionSuccessResponse(message="Playback started")


@mcp.tool()
async def pause_playback(device_id: str | None = None) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.pause_playback(device_id=device_id)
    return ActionSuccessResponse(message="Playback paused")


@mcp.tool()
async def add_to_queue(uri: str, device_id: str | None = None) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.add_to_queue(uri=uri, device_id=device_id)
    return ActionSuccessResponse(message=f"Added {uri} to queue")


@mcp.tool()
async def set_volume(volume_percent: int, device_id: str | None = None) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.volume(volume_percent=volume_percent, device_id=device_id)
    return ActionSuccessResponse(message=f"Volume set to {volume_percent}%")


@mcp.tool()
async def transfer_playback(device_id: str, force_play: bool = True) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.transfer_playback(device_id=device_id, force_play=force_play)
    return ActionSuccessResponse(message=f"Playback transferred to device {device_id}")


@mcp.tool()
async def search_spotify(
    query: str,
    type: str = "track",
    limit: int = 10,
    market: str | None = None,
) -> SearchResponse:
    spotify_client = get_spotify_client()
    return await spotify_client.search(q=query, type=type, limit=limit, market=market)


@mcp.tool()
async def get_saved_tracks(
    limit: int = 20,
    offset: int = 0,
    market: str | None = None,
) -> SavedTracksResponse:
    spotify_client = get_spotify_client()
    return await spotify_client.current_user_saved_tracks(limit=limit, offset=offset, market=market)

# brauche ich nicht diese methode
@mcp.tool()
async def check_saved_tracks(track_ids: list[str]):
    spotify_client = get_spotify_client()
    result = await spotify_client.current_user_saved_tracks_contains(tracks=track_ids)
    return {"tracks": track_ids, "saved": result}

# hier auch logishcen lookup für die tracks machen (cachen)
@mcp.tool()
async def save_tracks(track_ids: list[str]) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.current_user_saved_tracks_add(tracks=track_ids)
    return ActionSuccessResponse(message=f"Saved {len(track_ids)} track(s)")


@mcp.tool()
async def remove_saved_tracks(track_ids: list[str]) -> ActionSuccessResponse:
    spotify_client = get_spotify_client()
    await spotify_client.current_user_saved_tracks_delete(tracks=track_ids)
    return ActionSuccessResponse(message=f"Removed {len(track_ids)} track(s)")


@mcp.tool()
async def get_top_tracks(
    limit: int = 20,
    offset: int = 0,
    time_range: str = "medium_term",
) -> TopTracksResponse:
    spotify_client = get_spotify_client()
    return await spotify_client.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)


@mcp.tool()
async def get_recently_played(
    limit: int = 20,
    after: int | None = None,
    before: int | None = None,
) -> RecentlyPlayedResponse:
    spotify_client = get_spotify_client()
    return await spotify_client.current_user_recently_played(limit=limit, after=after, before=before)


@mcp.tool()
async def create_playlist(
    user_id: str,
    name: str,
    description: str = "",
    public: bool = True,
    collaborative: bool = False,
) -> SimplifiedPlaylist:
    spotify_client = get_spotify_client()
    return await spotify_client.user_playlist_create(
        user=user_id,
        name=name,
        description=description,
        public=public,
        collaborative=collaborative,
    )


@mcp.tool()
async def get_episode(episode_id: str, market: str | None = None) -> Episode:
    spotify_client = get_spotify_client()
    return await spotify_client.episode(episode_id=episode_id, market=market)


@mcp.tool()
async def get_show_episodes(
    show_id: str,
    limit: int = 20,
    offset: int = 0,
    market: str | None = None,
) -> ShowEpisodesResponse:
    spotify_client = get_spotify_client()
    return await spotify_client.show_episodes(
        show_id=show_id,
        limit=limit,
        offset=offset,
        market=market,
    )


if __name__ == "__main__":
    mcp.run()