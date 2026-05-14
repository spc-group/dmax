import httpx
import pytest
import stamina

from dmax import AsyncClient, Client
from dmax.processing import Workflow
from dmax.testing import maybe_await

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
async def test_get_workflow(httpx_mock, api):
    url = httpx.URL(
        f"{base_uri}/dm/workflowsByOwner/dummy_user/b'WlhoaGJYQnNaUzB3TVE9PQ=='"
    )
    httpx_mock.add_response(url=url, json=workflows[0])
    wf = await maybe_await(api.workflow(name="example-01"))
    assert wf.name == "example-01"
    assert "01-START" in wf.stages
    stage = wf.stages["01-START"]
    assert stage.command == "/bin/date +%Y%m%d%H%M%S"
    assert stage.output_variable_regular_expressions == ["(?P<timeStamp>.*)"]


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
async def test_add_new_workflow(httpx_mock, api):
    # url="/dm/workflows/addWorkflow
    new_workflow = Workflow(**workflows[0])
    url = httpx.URL(
        f"{base_uri}/dm/workflows/addWorkflow",
        params={
            "allowCurrentUsername": 0,
            "workflow": (
                "b'ZXlKdVlXMWxJam9pWlhoaGJYQnNaUzB3TVNJc0ltOTNibVZ5SWpvaVpIVnRiWGxmZFhObGNpSXNJblZ6WlhKZllXTmpiM1Z1ZENJNkltUjFiVzE1WDNWelpYSWlMQ0prWlhOamNtbHdkR2x2YmlJNklsZHZjbXRtYkc5M0lFVjRZVzF3YkdVZ01ERWlMQ0pwWkNJNklqWTVaakJqTUdJeE5EUXdPV0l4WVRjME1UZzFOR0psTmlJc0luTjBZV2RsY3lJNmV5SXdNUzFUVkVGU1ZDSTZleUpqYjIxdFlXNWtJam9pTDJKcGJpOWtZWFJsSUNzbFdTVnRKV1FsU0NWTkpWTWlMQ0p2ZFhSd2RYUmZkbUZ5YVdGaWJHVmZjbVZuZFd4aGNsOWxlSEJ5WlhOemFXOXVjeUk2V3lJb1AxQThkR2x0WlZOMFlXMXdQaTRxS1NKZGZTd2lNREl0VFV0RVNWSWlPbnNpWTI5dGJXRnVaQ0k2SWk5aWFXNHZiV3RrYVhJZ0xYQWdMM1J0Y0M5M2IzSnJabXh2ZHk0a2RHbHRaVk4wWVcxd0lpd2liM1YwY0hWMFgzWmhjbWxoWW14bFgzSmxaM1ZzWVhKZlpYaHdjbVZ6YzJsdmJuTWlPbHRkZlN3aU1ETXRSVU5JVHlJNmV5SmpiMjF0WVc1a0lqb2lMMkpwYmk5bFkyaHZJRnhjWENKVFZFRlNWQ0JLVDBJZ1NVUTZJQ1JwWkZ4Y1hDSWdQaUF2ZEcxd0wzZHZjbXRtYkc5M0xpUjBhVzFsVTNSaGJYQXZKR2xrTG05MWRDSXNJbTkxZEhCMWRGOTJZWEpwWVdKc1pWOXlaV2QxYkdGeVgyVjRjSEpsYzNOcGIyNXpJanBiWFgwc0lqQTBMVTFFTlZOVlRTSTZleUpqYjIxdFlXNWtJam9pTDJKcGJpOXRaRFZ6ZFcwZ0pHWnBiR1ZRWVhSb0lId2dZM1YwSUMxbU1TQXRaRnhjWENJZ1hGeGNJaUlzSW05MWRIQjFkRjkyWVhKcFlXSnNaVjl5WldkMWJHRnlYMlY0Y0hKbGMzTnBiMjV6SWpwYklpZy9VRHh0WkRWVGRXMCtMaW9wSWwxOUxDSXdOUzFGUTBoUElqcDdJbU52YlcxaGJtUWlPaUpsWTJodklGeGNYQ0pHU1V4RklDUm1hV3hsVUdGMGFDQk5SRFVnVTFWTk9pQWtiV1ExVTNWdFhGeGNJaUErUGlBdmRHMXdMM2R2Y210bWJHOTNMaVIwYVcxbFUzUmhiWEF2Skdsa0xtOTFkQ0lzSW05MWRIQjFkRjkyWVhKcFlXSnNaVjl5WldkMWJHRnlYMlY0Y0hKbGMzTnBiMjV6SWpwYlhYMHNJakEyTFVSUFRrVWlPbnNpWTI5dGJXRnVaQ0k2SWk5aWFXNHZaV05vYnlCY1hGd2lVMVJQVUNCS1QwSWdTVVE2SUNScFpGeGNYQ0lnUGo0Z0wzUnRjQzkzYjNKclpteHZkeTRrZEdsdFpWTjBZVzF3THlScFpDNXZkWFFpTENKdmRYUndkWFJmZG1GeWFXRmliR1ZmY21WbmRXeGhjbDlsZUhCeVpYTnphVzl1Y3lJNlcxMTlmWDA9'"
            ),
        },
    )
    httpx_mock.add_response(url=url, method="POST", json=workflows[0])
    wf = await maybe_await(api.add_workflow(workflow=new_workflow))
    assert wf.name == "example-01"
    assert "01-START" in wf.stages
    stage = wf.stages["01-START"]
    assert stage.command == "/bin/date +%Y%m%d%H%M%S"
    assert stage.output_variable_regular_expressions == ["(?P<timeStamp>.*)"]


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_update_workflow(httpx_mock, api):
    # Mock for retrieving the existing workflow
    url = httpx.URL(
        f"{base_uri}/dm/workflowsByOwner/dummy_user/b'WlhoaGJYQnNaUzB3TVE9PQ=='"
    )
    httpx_mock.add_response(url=url, json=workflows[0])
    # url="/dm/workflows/addWorkflow
    url = httpx.URL(
        f"{base_uri}/dm/workflows/updateWorkflow",
        params={
            "allowCurrentUsername": 0,
            "workflow": (
                "b'ZXlKdVlXMWxJam9pWlhoaGJYQnNaUzB3TVNJc0ltOTNibVZ5SWpvaVpIVnRiWGxmZFhObGNpSXNJblZ6WlhKZllXTmpiM1Z1ZENJNkltUjFiVzE1WDNWelpYSWlMQ0prWlhOamNtbHdkR2x2YmlJNkltRWdZbVYwZEdWeUlHUmxjMk55YVhCMGFXOXVJaXdpYVdRaU9pSTJPV1l3WXpCaU1UUTBNRGxpTVdFM05ERTROVFJpWlRZaUxDSnpkR0ZuWlhNaU9uc2lNREV0VTFSQlVsUWlPbnNpWTI5dGJXRnVaQ0k2SWk5aWFXNHZaR0YwWlNBckpWa2xiU1ZrSlVnbFRTVlRJaXdpYjNWMGNIVjBYM1poY21saFlteGxYM0psWjNWc1lYSmZaWGh3Y21WemMybHZibk1pT2xzaUtEOVFQSFJwYldWVGRHRnRjRDR1S2lraVhYMHNJakF5TFUxTFJFbFNJanA3SW1OdmJXMWhibVFpT2lJdlltbHVMMjFyWkdseUlDMXdJQzkwYlhBdmQyOXlhMlpzYjNjdUpIUnBiV1ZUZEdGdGNDSXNJbTkxZEhCMWRGOTJZWEpwWVdKc1pWOXlaV2QxYkdGeVgyVjRjSEpsYzNOcGIyNXpJanBiWFgwc0lqQXpMVVZEU0U4aU9uc2lZMjl0YldGdVpDSTZJaTlpYVc0dlpXTm9ieUJjWEZ3aVUxUkJVbFFnU2s5Q0lFbEVPaUFrYVdSY1hGd2lJRDRnTDNSdGNDOTNiM0pyWm14dmR5NGtkR2x0WlZOMFlXMXdMeVJwWkM1dmRYUWlMQ0p2ZFhSd2RYUmZkbUZ5YVdGaWJHVmZjbVZuZFd4aGNsOWxlSEJ5WlhOemFXOXVjeUk2VzExOUxDSXdOQzFOUkRWVFZVMGlPbnNpWTI5dGJXRnVaQ0k2SWk5aWFXNHZiV1ExYzNWdElDUm1hV3hsVUdGMGFDQjhJR04xZENBdFpqRWdMV1JjWEZ3aUlGeGNYQ0lpTENKdmRYUndkWFJmZG1GeWFXRmliR1ZmY21WbmRXeGhjbDlsZUhCeVpYTnphVzl1Y3lJNld5SW9QMUE4YldRMVUzVnRQaTRxS1NKZGZTd2lNRFV0UlVOSVR5STZleUpqYjIxdFlXNWtJam9pWldOb2J5QmNYRndpUmtsTVJTQWtabWxzWlZCaGRHZ2dUVVExSUZOVlRUb2dKRzFrTlZOMWJWeGNYQ0lnUGo0Z0wzUnRjQzkzYjNKclpteHZkeTRrZEdsdFpWTjBZVzF3THlScFpDNXZkWFFpTENKdmRYUndkWFJmZG1GeWFXRmliR1ZmY21WbmRXeGhjbDlsZUhCeVpYTnphVzl1Y3lJNlcxMTlMQ0l3TmkxRVQwNUZJanA3SW1OdmJXMWhibVFpT2lJdlltbHVMMlZqYUc4Z1hGeGNJbE5VVDFBZ1NrOUNJRWxFT2lBa2FXUmNYRndpSUQ0K0lDOTBiWEF2ZDI5eWEyWnNiM2N1SkhScGJXVlRkR0Z0Y0M4a2FXUXViM1YwSWl3aWIzVjBjSFYwWDNaaGNtbGhZbXhsWDNKbFozVnNZWEpmWlhod2NtVnpjMmx2Ym5NaU9sdGRmWDE5'"
            ),
        },
    )
    httpx_mock.add_response(url=url, method="PUT", json=workflows[0])
    update = {"description": "a better description"}
    await maybe_await(api.update_workflow(name="example-01", update=update))


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
