from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExternalUrls(BaseModel):
    spotify: str


class Image(BaseModel):
    url: str
    height: int | None = None
    width: int | None = None


class Followers(BaseModel):
    href: str | None = None
    total: int


class ExternalIds(BaseModel):
    isrc: str | None = None
    ean: str | None = None
    upc: str | None = None


class SimplifiedArtist(BaseModel):
    id: str
    name: str
    type: str
    uri: str
    external_urls: ExternalUrls
    href: str


class Artist(SimplifiedArtist):
    followers: Followers | None = None
    genres: list[str] = Field(default_factory=list)
    images: list[Image] = Field(default_factory=list)
    popularity: int | None = None


class SimplifiedAlbum(BaseModel):
    id: str
    name: str
    type: str
    uri: str
    external_urls: ExternalUrls
    href: str
    album_type: str
    total_tracks: int
    release_date: str
    release_date_precision: str
    images: list[Image] = Field(default_factory=list)
    artists: list[SimplifiedArtist] = Field(default_factory=list)


class Album(SimplifiedAlbum):
    genres: list[str] = Field(default_factory=list)
    label: str | None = None
    popularity: int | None = None
    copyrights: list[dict[str, str]] = Field(default_factory=list)


class Track(BaseModel):
    id: str
    name: str
    type: str
    uri: str
    external_urls: ExternalUrls
    href: str
    duration_ms: int
    explicit: bool
    is_local: bool
    popularity: int | None = None
    preview_url: str | None = None
    track_number: int
    disc_number: int
    external_ids: ExternalIds | None = None
    artists: list[SimplifiedArtist] = Field(default_factory=list)
    album: SimplifiedAlbum | None = None
    available_markets: list[str] = Field(default_factory=list)
    is_playable: bool | None = None


class Device(BaseModel):
    id: str
    name: str
    type: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    volume_percent: int | None = None
    supports_volume: bool


class Context(BaseModel):
    type: str
    href: str
    external_urls: ExternalUrls
    uri: str


class PlaybackState(BaseModel):
    device: Device
    repeat_state: str
    shuffle_state: bool
    timestamp: int
    progress_ms: int | None = None
    is_playing: bool
    item: Track | None = None
    currently_playing_type: str
    context: Context | None = None


class SimplifiedShow(BaseModel):
    id: str
    name: str
    type: str
    uri: str
    external_urls: ExternalUrls
    href: str
    description: str
    publisher: str
    images: list[Image] = Field(default_factory=list)
    explicit: bool
    total_episodes: int | None = None


class Episode(BaseModel):
    id: str
    name: str
    type: str
    uri: str
    external_urls: ExternalUrls
    href: str
    description: str
    duration_ms: int
    explicit: bool
    release_date: str
    release_date_precision: str
    language: str | None = None
    languages: list[str] = Field(default_factory=list)
    is_playable: bool
    images: list[Image] = Field(default_factory=list)
    show: SimplifiedShow | None = None
    audio_preview_url: str | None = None


class DevicesResponse(BaseModel):
    devices: list[Device] = Field(default_factory=list)


class SavedTrack(BaseModel):
    added_at: datetime
    track: Track


class PagingObject(BaseModel):
    href: str
    limit: int
    offset: int
    total: int
    next: str | None = None
    previous: str | None = None


class SavedTracksResponse(PagingObject):
    items: list[SavedTrack] = Field(default_factory=list)


class TopTracksResponse(PagingObject):
    items: list[Track] = Field(default_factory=list)


class TopArtistsResponse(PagingObject):
    items: list[Artist] = Field(default_factory=list)


class RecentlyPlayedTrack(BaseModel):
    track: Track
    played_at: datetime
    context: Context | None = None


class RecentlyPlayedResponse(BaseModel):
    items: list[RecentlyPlayedTrack] = Field(default_factory=list)
    next: str | None = None
    cursors: dict[str, str] | None = None
    limit: int
    href: str


class ShowEpisodesResponse(PagingObject):
    items: list[Episode] = Field(default_factory=list)


class SearchResponse(BaseModel):
    tracks: PagingObject | None = None
    artists: PagingObject | None = None
    albums: PagingObject | None = None
    playlists: PagingObject | None = None
    shows: PagingObject | None = None
    episodes: PagingObject | None = None


class PlaylistTrack(BaseModel):
    added_at: datetime
    added_by: dict[str, Any]
    is_local: bool
    track: Track | Episode


class SimplifiedPlaylist(BaseModel):
    id: str
    name: str
    type: str
    uri: str
    external_urls: ExternalUrls
    href: str
    public: bool | None = None
    collaborative: bool
    description: str | None = None
    images: list[Image] = Field(default_factory=list)
    owner: dict[str, Any]
    snapshot_id: str
    tracks: dict[str, Any]