import httpx
import pytest
import stamina

from dmax import AsyncClient, Client
from dmax.testing import maybe_await

"""

 ✘  ~/research-spc/aps-dm-api  pixi run production/bin/dm-list-processing-jobs
sm.host='https://s25idcdm.xray.aps.anl.gov:55536'
url="/dm/processingJobsByOwner/s25idcuser?queryDict=b'ZTMwPQo='&skip=0&limit=5000&keyList=b'SWtSRlJrRlZURlFpCg=='"
data={}
responseData=b'[]'


 ~/research-spc/aps-dm-api  pixi run production/bin/dm-start-processing-job --workflow-name example-01 run_uid:12345
sm.host='https://s25idcdm.xray.aps.anl.gov:55536'
url="/dm/processingJobsByWorkflow/s25idcuser/b'WlhoaGJYQnNaUzB3TVE9PQo='/startProcessingJob?argsDict=b'ZXlKeWRXNWZkV2xrSWpvZ0lqRXlNelExSW4wPQo='"
data={}
responseData=b'{"run_uid": "12345", "workflow": {"name": "example-01", "owner": "s25idcuser", "userAccount": "s25idcuser", "stages": {"01-START": {"command": "/bin/date +%Y%m%d%H%M%S", "outputVariableRegexList": ["(?P<timeStamp>.*)"]}, "02-MKDIR": {"command": "/bin/mkdir -p /tmp/workflow.$timeStamp"}, "03-ECHO": {"command": "/bin/echo \\"START JOB ID: $id\\" > /tmp/workflow.$timeStamp/$id.out"}, "04-MD5SUM": {"command": "/bin/md5sum $filePath | cut -f1 -d\\" \\"", "outputVariableRegexList": ["(?P<md5Sum>.*)"]}, "05-ECHO": {"command": "echo \\"FILE $filePath MD5 SUM: $md5Sum\\" >> /tmp/workflow.$timeStamp/$id.out"}, "06-DONE": {"command": "/bin/echo \\"STOP JOB ID: $id\\" >> /tmp/workflow.$timeStamp/$id.out"}}, "description": "Workflow Example 01", "id": "69f0c0b14409b1a741854be6"}, "owner": "s25idcuser", "id": "3a4c943e-d01f-418e-ba36-76e962770987", "submissionTime": 1778252821.8895876, "submissionTimestamp": "2026/05/08 10:07:01 CDT", "countFiles": 0, "status": "pending"}'
id=3a4c943e-d01f-418e-ba36-76e962770987 owner=s25idcuser status=pending
"""

workflows = [
    {
        "name": "example-01",
        "owner": "dummy_user",
        "userAccount": "dummy_user",
        "stages": {
            "01-START": {
                "command": "/bin/date +%Y%m%d%H%M%S",
                "outputVariableRegexList": ["(?P<timeStamp>.*)"],
            },
            "02-MKDIR": {"command": "/bin/mkdir -p /tmp/workflow.$timeStamp"},
            "03-ECHO": {
                "command": (
                    '/bin/echo \\"START JOB ID: $id\\" > /tmp/workflow.$timeStamp/$id.out'
                )
            },
            "04-MD5SUM": {
                "command": '/bin/md5sum $filePath | cut -f1 -d\\" \\"',
                "outputVariableRegexList": ["(?P<md5Sum>.*)"],
            },
            "05-ECHO": {
                "command": (
                    'echo \\"FILE $filePath MD5 SUM: $md5Sum\\" >> /tmp/workflow.$timeStamp/$id.out'
                )
            },
            "06-DONE": {
                "command": (
                    '/bin/echo \\"STOP JOB ID: $id\\" >> /tmp/workflow.$timeStamp/$id.out'
                )
            },
        },
        "description": "Workflow Example 01",
        "id": "69f0c0b14409b1a741854be6",
    }
]


jobs = [
    {
        "countFiles": 0,
        "endTime": 1778252804.1749194,
        "endTimestamp": "2026/05/08 10:06:44 CDT",
        "errorMessage": "Invalid input file specification.",
        "id": "f57af209-fabe-49f2-bed3-5cae13186bc7",
        "owner": "s25idcuser",
        "runTime": 0.00031828880310058594,
        "startTime": 1778252804.174601,
        "startTimestamp": "2026/05/08 10:06:44 CDT",
        "status": "failed",
        "submissionTime": 1778252804.1145132,
        "submissionTimestamp": "2026/05/08 10:06:44 CDT",
        "workflow": {
            "description": "Workflow Example 01",
            "id": "69f0c0b14409b1a741854be6",
            "name": "example-01",
            "owner": "s25idcuser",
            "stages": {
                "01-START": {
                    "command": "/bin/date +%Y%m%d%H%M%S",
                    "outputVariableRegexList": ["(?P<timeStamp>.*)"],
                },
                "02-MKDIR": {"command": "/bin/mkdir -p " "/tmp/workflow.$timeStamp"},
                "03-ECHO": {
                    "command": (
                        '/bin/echo "START JOB ID: '
                        '$id" > '
                        "/tmp/workflow.$timeStamp/$id.out"
                    )
                },
                "04-MD5SUM": {
                    "command": "/bin/md5sum $filePath | " 'cut -f1 -d" "',
                    "outputVariableRegexList": ["(?P<md5Sum>.*)"],
                },
                "05-ECHO": {
                    "command": (
                        'echo "FILE $filePath MD5 '
                        'SUM: $md5Sum" >> '
                        "/tmp/workflow.$timeStamp/$id.out"
                    )
                },
                "06-DONE": {
                    "command": (
                        '/bin/echo "STOP JOB ID: $id" '
                        ">> "
                        "/tmp/workflow.$timeStamp/$id.out"
                    )
                },
            },
            "userAccount": "s25idcuser",
        },
    },
    {
        "countFiles": 0,
        "endTime": 1778252821.8917148,
        "endTimestamp": "2026/05/08 10:07:01 CDT",
        "errorMessage": "Invalid input file specification.",
        "id": "3a4c943e-d01f-418e-ba36-76e962770987",
        "owner": "s25idcuser",
        "runTime": 0.0002357959747314453,
        "run_uid": "12345",
        "startTime": 1778252821.891479,
        "startTimestamp": "2026/05/08 10:07:01 CDT",
        "status": "failed",
        "submissionTime": 1778252821.8895876,
        "submissionTimestamp": "2026/05/08 10:07:01 CDT",
        "workflow": {
            "description": "Workflow Example 01",
            "id": "69f0c0b14409b1a741854be6",
            "name": "example-01",
            "owner": "s25idcuser",
            "stages": {
                "01-START": {
                    "command": "/bin/date +%Y%m%d%H%M%S",
                    "outputVariableRegexList": ["(?P<timeStamp>.*)"],
                },
                "02-MKDIR": {"command": "/bin/mkdir -p " "/tmp/workflow.$timeStamp"},
                "03-ECHO": {
                    "command": (
                        '/bin/echo "START JOB ID: '
                        '$id" > '
                        "/tmp/workflow.$timeStamp/$id.out"
                    )
                },
                "04-MD5SUM": {
                    "command": "/bin/md5sum $filePath | " 'cut -f1 -d" "',
                    "outputVariableRegexList": ["(?P<md5Sum>.*)"],
                },
                "05-ECHO": {
                    "command": (
                        'echo "FILE $filePath MD5 '
                        'SUM: $md5Sum" >> '
                        "/tmp/workflow.$timeStamp/$id.out"
                    )
                },
                "06-DONE": {
                    "command": (
                        '/bin/echo "STOP JOB ID: $id" '
                        ">> "
                        "/tmp/workflow.$timeStamp/$id.out"
                    )
                },
            },
            "userAccount": "s25idcuser",
        },
    },
]


[
    {
        "id": "f57af209-fabe-49f2-bed3-5cae13186bc7",
        "owner": "s25idcuser",
        "status": "failed",
        "startTime": 1778252804.174601,
        "endTime": 1778252804.1749194,
        "runTime": 0.00031828880310058594,
        "startTimestamp": "2026/05/08 10:06:44 CDT",
        "endTimestamp": "2026/05/08 10:06:44 CDT",
        "errorMessage": "Invalid input file specification.",
    },
    {
        "id": "3a4c943e-d01f-418e-ba36-76e962770987",
        "owner": "s25idcuser",
        "status": "failed",
        "startTime": 1778252821.891479,
        "endTime": 1778252821.8917148,
        "runTime": 0.0002357959747314453,
        "startTimestamp": "2026/05/08 10:07:01 CDT",
        "endTimestamp": "2026/05/08 10:07:01 CDT",
        "errorMessage": "Invalid input file specification.",
    },
]

base_uri = "http://localhost:12345"


@pytest.fixture()
def api(request):
    stamina.set_testing(True)
    if getattr(request, "param", "async") == "async":
        client = AsyncClient(
            username="dummy_user",
            password="",
            station_name="25IDC",
            processing_uri=base_uri,
        )
    else:
        client = Client(
            username="dummy_user",
            password="",
            station_name="25IDC",
            processing_uri=base_uri,
        )
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_get_workflows(httpx_mock, api):
    # host='https://s25idcdm.xray.aps.anl.gov:55536'
    # url="/dm/workflowsByOwner/s25idcuser?queryDict=b'ZTMwPQo='"
    url = httpx.URL(
        f"{base_uri}/dm/workflowsByOwner/dummy_user",
        params={"queryDict": "b'ZTMwPQ=='"},
    )
    httpx_mock.add_response(url=url, json=workflows)
    workflows_ = await maybe_await(api.workflows())
    (wf,) = workflows_
    assert wf.name == "example-01"
    assert "01-START" in wf.stages
    stage = wf.stages["01-START"]
    assert stage.command == "/bin/date +%Y%m%d%H%M%S"
    assert stage.output_variable_regular_expressions == ["(?P<timeStamp>.*)"]


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_get_processing_jobs(httpx_mock, api):
    url = httpx.URL(
        f"{base_uri}/dm/processingJobsByOwner/dummy_user",
        params={
            "queryDict": "b'ZTMwPQ=='",  # b'{}'
            "skip": 21,
            "limit": 2000,
            "keyList": "b'SWtGTVRDST0='",  # b'"DEFAULT"'
        },
    )
    httpx_mock.add_response(url=url, json=jobs)
    jobs_ = await maybe_await(api.processing_jobs(offset=21, limit=2000))
    job0, job1 = jobs_
    assert job0.file_count == 0
    assert job0.end.year == 2026
    assert job0.error_message == "Invalid input file specification."
    assert job0.id == "f57af209-fabe-49f2-bed3-5cae13186bc7"
    assert job0.workflow.name == "example-01"


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_submit_processing_job(httpx_mock, api):
    workflow_name = b"WlhoaGJYQnNaUzB3TVE9PQ=="  # b'example-01'
    url = httpx.URL(
        f"{base_uri}/dm/processingJobsByWorkflow/dummy_user/{workflow_name}/startProcessingJob",
        params={
            "argsDict": (
                b"ZXlKeWRXNWZkV2xrSWpvZ0lqRXlNelExSW4wPQ=="  # b'{"run_uid": "12345"}'
            )
        },
    )
    httpx_mock.add_response(url=url, json=jobs[0], method="POST")
    job = await maybe_await(
        api.submit_processing_job(workflow="example-01", run_uid="12345")
    )
    assert job.workflow.name == "example-01"
