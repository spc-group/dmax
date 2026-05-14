"""Routines for interacting with the remote procedure call API."""

import datetime as dt
import json
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING

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
    duration: float = Field(alias="runTime", default=MISSING)
    start: dt.datetime = Field(alias="endTime")
    end: dt.datetime = Field(alias="endTime", default=MISSING)
    status: str
    submitted: dt.datetime = Field(alias="submissionTime")
    workflow: Workflow


def request_workflows(owner: str, context):
    url = f"/workflowsByOwner/{owner}"
    json_data = yield context.get(url, params={"queryDict": str(encode("{}"))})
    data = json.loads(json_data)
    return [Workflow(**datum) for datum in data]


def request_workflow(name: str, owner: str, context):
    url = f"/workflowsByOwner/{owner}/{encode(name)!r}"
    json_data = yield context.get(url)
    return Workflow(**json.loads(json_data))


def post_workflow(spec: Workflow, context):
    url = "/workflows/addWorkflow"
    params = {"allowCurrentUsername": 0, "workflow": encode(spec.model_dump_json())}
    json_data = yield context.post(url, params=params)
    return Workflow(**json.loads(json_data))


def put_workflow(name: str, spec: Workflow, context):
    # url = "/dm/workflows/updateWorkflow?workflow"
    url = "/workflows/updateWorkflow"
    params = {"allowCurrentUsername": 0, "workflow": encode(spec.model_dump_json())}
    json_data = yield context.put(url, params=params)
    return Workflow(**json.loads(json_data))


def patch_workflow(name: str, update: Mapping[str, Any], owner: str, context):
    old_wf = yield from request_workflow(name=name, owner=owner, context=context)
    new_wf = old_wf.model_copy(update=update)
    return (yield from put_workflow(name=new_wf.name, spec=new_wf, context=context))


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
