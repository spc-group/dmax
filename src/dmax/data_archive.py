import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING

from .context import AsyncContext, RequestGenerator, SyncContext, encode


class DataArchiveQueue(BaseModel):
    file_count: int = Field(alias="countFiles", default=0)
    data_directory: str = Field(alias="dataDirectory")
    experiment_name: str = Field(alias="experimentName")
    station_name: str = Field(alias="experimentStationName")
    id: str
    processed_file_count: int = Field(alias="nProcessedFiles", default=0)
    processing_errors_count: int = Field(alias="nProcessingErrors", default=0)
    skip_file_path_pattern: str = Field(alias="skipFilePathPattern", default=MISSING)
    start: float = Field(alias="startTime")
    status: str = Field(alias="status")
    storage_directory: str = Field(alias="storageDirectory")
    storage_host: str = Field(alias="storageHost")
    storage_url: str = Field(alias="storageUrl")
    workflow_job_owner: str = Field(alias="workflowJobOwner")


def post_daq(
    source_directory: Path | str,
    experiment_name: str,
    context: SyncContext | AsyncContext,
    skip: str | None = None,
) -> RequestGenerator[DataArchiveQueue]:
    task_info = {}
    if skip is not None:
        task_info["skipFilePathPattern"] = skip
    params = {"taskInfo": str(encode(json.dumps(task_info)))}
    source_dir = str(source_directory)
    url = f"/experimentsByName/{encode(experiment_name)!r}/startDaq/{encode(source_dir)!r}"
    json_data = yield context.post(url, params=params)
    data = json.loads(json_data)
    return DataArchiveQueue(**data)
