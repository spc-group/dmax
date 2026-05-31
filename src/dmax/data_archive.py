import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING

from .context import AsyncContext, SyncContext, encode


class DataArchiveQueue(BaseModel):
    file_count: int = Field(alias="countFiles", default=0)
    data_directory: str = Field(alias="dataDirectory")
    experiment_name: str = Field(alias="experimentName")
    station_name: str = Field(alias="experimentStationName")
    id: str
    processed_file_count: int = Field(alias="nProcessedFiles", default=0)
    processing_errors_count: int = Field(alias="nProcessingErrors", default=0)
    start: float  = Field(alias="startTime")
    status: str =Field(alias="status")
    storage_directory: str =Field(alias="storageDirectory")
    storage_host: str =Field(alias="storageHost")
    storage_url: str =Field(alias="storageUrl")
    workflow_job_owner: str = Field(alias="workflowJobOwner")



def post_daq(
    source_directory: Path | str,
    experiment_name: str,
    owner: str,
    context: SyncContext | AsyncContext,
):
    url = f"/experimentsByName/{encode(experiment_name)!r}/startDaq/{encode(source_directory)!r}"
    json_data = yield context.post(url)
    data = json.loads(json_data)
    print(data)
    return DataArchiveQueue(**data)
    return [Experiment(**datum) for datum in data]

