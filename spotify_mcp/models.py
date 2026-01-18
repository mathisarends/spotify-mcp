from datetime import datetime
from pydantic import BaseModel, Field


class SimplifiedArtist(BaseModel):
    id: str
    name: str


class SimplifiedAlbum(BaseModel):
    id: str
    name: str
    uri: str
    artists: list[SimplifiedArtist] = Field(default_factory=list)


class Track(BaseModel):
    id: str
    name: str
    uri: str
    artists: list[SimplifiedArtist] = Field(default_factory=list)
    duration_ms: int
    album: SimplifiedAlbum | None = None


class Device(BaseModel):
    id: str
    name: str
    is_active: bool
    volume_percent: int | None = None


class PlaybackState(BaseModel):
    is_playing: bool
    progress_ms: int | None = None
    device: Device
    item: Track | None = None


class DevicesResponse(BaseModel):
    devices: list[Device] = Field(default_factory=list)


class PagingObject(BaseModel):
    total: int
    limit: int
    offset: int


class RecentlyPlayedTrack(BaseModel):
    track: Track
    played_at: datetime


class RecentlyPlayedResponse(BaseModel):
    items: list[RecentlyPlayedTrack] = Field(default_factory=list)
    limit: int


class TracksSearchResult(PagingObject):
    items: list[Track] = Field(default_factory=list)


class AlbumsSearchResult(PagingObject):
    items: list[SimplifiedAlbum] = Field(default_factory=list)


class SearchResponse(BaseModel):
    tracks: TracksSearchResult | None = None
    albums: AlbumsSearchResult | None = None