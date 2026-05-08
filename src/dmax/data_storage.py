import datetime as dt
import json

from pydantic import BaseModel, Field


class Storage(BaseModel):
    description: str = ""
    name: str
    id: int


class ExperimentStation(BaseModel):
    description: str = ""
    name: str
    id: int


class ExperimentType(BaseModel):
    description: str = ""
    name: str
    id: int


class Experiment(BaseModel):
    name: str
    description: str = ""
    id: int
    primary_storage: Storage = Field(alias="primaryStorage")
    station: ExperimentStation = Field(alias="experimentStation")
    type: ExperimentType = Field(alias="experimentType")
    created: dt.datetime = Field(alias="createDate")
    updated: dt.datetime = Field(alias="updateDate")
    started: dt.datetime = Field(alias="startDate")
    ended: dt.datetime = Field(alias="endDate")
    auth_group_name: str = ""


def request_experiments(station_name: str, context):
    """Retrieve experiments defined in the data storage system."""
    url = f"/experimentsByStation/{station_name}"
    json_data = yield context.get(url)
    # response = yield context.get(url, params=params)
    data = json.loads(json_data)
    return [Experiment(**datum) for datum in data]
