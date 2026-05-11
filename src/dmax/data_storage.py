import datetime as dt
import json
from typing import Sequence

from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING

from .context import encode


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
    start: dt.datetime = Field(alias="startDate")
    end: dt.datetime = Field(alias="endDate")
    auth_group_name: str = ""
    # These values are only provided for individual experiments, but
    # will be abset when getting a list of experiments
    # Field(default=MISSING, alias="")
    users: Sequence[str] = Field(default=MISSING, alias="experimentUsernameList")
    root_path: str = Field(default=MISSING, alias="rootPath")
    storage_path: str = Field(default=MISSING, alias="storageDirectory")
    storage_uri: str = Field(default=MISSING, alias="storageUrl")
    admin_account: str = Field(default=MISSING, alias="beamlineAdminAccount")
    user_account: str = Field(default=MISSING, alias="beamlineUserAccount")
    analysis_path: str = Field(default=MISSING, alias="analysisDirectory")
    analysis_path_path_is_frozen: bool = Field(
        default=MISSING, alias="analysisDirectoryFrozen"
    )
    data_path: str = Field(default=MISSING, alias="dataDirectory")
    data_path_path_is_frozen: bool = Field(default=MISSING, alias="dataDirectoryFrozen")
    system_path: str = Field(default=MISSING, alias="systemDirectory")
    folders_are_managed: bool = Field(
        default=MISSING, alias="managedDirectoryStructure"
    )


def request_experiments(station_name: str, context):
    """Retrieve experiments defined in the data storage system."""
    url = f"/experimentsByStation/{station_name}"
    json_data = yield context.get(url)
    # response = yield context.get(url, params=params)
    data = json.loads(json_data)
    return [Experiment(**datum) for datum in data]


def request_experiment(id: str, name: str, station_name: str, context):
    """Retrieve a single experiment, either by id or name."""
    if id != "":
        url = f"/experimentsById/{id}"
    elif name != "":
        url = f"/experimentsByName/{encode(name)!r}/{station_name}"
    else:
        raise TypeError("Either *name* or *id* is required.")
    json_data = yield context.get(url)
    # response = yield context.get(url, params=params)
    data = json.loads(json_data)
    return Experiment(**data)
