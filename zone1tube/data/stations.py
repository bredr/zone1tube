from pydantic import BaseModel, TypeAdapter


class Destination(BaseModel):
    name: str
    line_colour: str
    line_stripe: str
    time: int
    longitude: float
    latitude: float
    station_id: int
    line_name: str
    line_id: int


class Station(BaseModel):
    name: str
    total_lines: int
    id: int
    longitude: float
    latitude: float
    rail: int
    zone: float
    destinations: list[Destination]


Stations = TypeAdapter(list[Station])
