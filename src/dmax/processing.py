"""Routines for interacting with the remote procedure call API."""

import datetime as dt
import json
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field

from .context import RequestGenerator, encode


class Stage(BaseModel):
    command: str
    output_variable_regular_expressions: Sequence[str] = Field(
        default=[], alias="outputVariableRegexList"
    )


class Workflow(BaseModel):
    name: str
    owner: str
    user_account: str = Field(alias="userAccount")
    description: str
    id: str
    stages: Mapping[str, Stage]


class Job(BaseModel):
    file_count: int = Field(alias="countFiles")
    error_message: str = Field(alias="errorMessage", default="")
    id: str
    owner: str
    duration: float = Field(alias="runTime")
    start: dt.datetime = Field(alias="endTime")
    end: dt.datetime = Field(alias="endTime")
    status: str
    submitted: dt.datetime = Field(alias="submissionTime")
    workflow: Workflow


def request_workflows(owner: str, context):
    url = f"/workflowsByOwner/{owner}"
    json_data = yield context.get(url, params={"queryDict": str(encode("{}"))})
    data = json.loads(json_data)
    return [Workflow(**datum) for datum in data]


def request_jobs(
    owner: str, limit: int, offset: int, context
) -> RequestGenerator[list[Job]]:
    """Retrieve a list of jobs from the processing API.

    Parameters
    ==========
    owner
      The username used to lookup jobs.
    limit
      The maximum number of jobs entries to fetch.
    offset
      Where in the list of jobs to start.
    context
      The HTTP context used for generating requests.
    """
    url = f"/processingJobsByOwner/{owner}"
    params = {
        "queryDict": str(encode("{}")),
        "skip": offset,
        "limit": limit,
        "keyList": str(encode('"ALL"')),
    }
    json_data = yield context.get(url, params=params)
    data = json.loads(json_data)
    return [Job(**datum) for datum in data]


def submit_job(
    workflow: str,
    job_args: Mapping[str, Any],
    owner: str,
    context,
):
    """Retrieve a list of jobs from the processing API.

    Parameters
    ==========
    workflow
      The name of the workflow to execute.
    **kwargs
      Variables to pass to the job.
    owner
      The username used to lookup jobs.
    context
      The HTTP context used for generating requests.
    """
    url = f"/processingJobsByWorkflow/{owner}/{encode(workflow)!r}/startProcessingJob"
    params = {"argsDict": str(encode(json.dumps(job_args)))}
    json_data = yield context.post(url, params=params)
    data = json.loads(json_data)
    return Job(**data)
