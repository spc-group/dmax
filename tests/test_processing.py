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


failed_job = {
    # sm.host='https://s25idcdm.xray.aps.anl.gov:55536'
    # url='/dm/processingJobsByOwner/s25idcuser/7e01fb97-44b1-4b7f-b1ca-d08624eb8c77'
    # 'data={}'
    # method='GET'
    # contentType='html'
    # response=<http.client.HTTPResponse object at 0x7efce40c6c20>
    "countFiles": 1,
    "endTime": 1778850780.4493127,
    "endTimestamp": "2026/05/15 08:13:00 CDT",
    "filePath": "/dev/null",
    "id": "7e01fb97-44b1-4b7f-b1ca-d08624eb8c77",
    "owner": "s25idcuser",
    "runTime": 14.460897207260132,
    "run_uid": "4ddd5c94-0825-4ab8-b1b5-12e8e5d66a48",
    "stage": "030-EXPORT",
    "startTime": 1778850765.9884155,
    "startTimestamp": "2026/05/15 08:12:45 CDT",
    "status": "failed",
    "submissionTime": 1778850765.985844,
    "submissionTimestamp": "2026/05/15 08:12:45 CDT",
    "target_folder": "/gdata/dm/25IDC/commissioning-2026-C2",
    "timeStamp": "20260515081246",
    "workflow": {
        "description": (
            "Processing for a Bluesky scan that has no "
            "significant data processing needs"
        ),
        "id": "6a03718401668a9aaf71ba47",
        "name": "simple",
        "owner": "s25idcuser",
        "stages": {
            "010-START": {
                "childProcesses": {
                    "0": {
                        "childProcessNumber": 0,
                        "command": (
                            "/usr/bin/sudo "
                            "-u "
                            "s25idcuser "
                            "-- "
                            "/bin/date "
                            "+%Y%m%d%H%M%S"
                        ),
                        "endTime": 1778850766.0461721,
                        "exitStatus": 0,
                        "runTime": 0.053916215896606445,
                        "stageId": "010-START",
                        "startTime": 1778850765.992256,
                        "status": "done",
                        "stdErr": "",
                        "stdOut": "20260515081246\n",
                        "submitTime": 1778850765.9913614,
                        "userAccount": "s25idcuser",
                        "workingDir": None,
                    }
                },
                "command": "/bin/date +%Y%m%d%H%M%S",
                "nCompletedChildProcesses": 1,
                "nQueuedChildProcesses": 0,
                "nRunningChildProcesses": 0,
                "outputVariableRegexList": ["(?P<timeStamp>.*)"],
            },
            "020-FIT_FLUORESCENCE": {
                "childProcesses": {
                    "1": {
                        "childProcessNumber": 1,
                        "command": (
                            "/usr/bin/sudo "
                            "-u "
                            "s25idcuser "
                            "-- "
                            "/APSshare/bin/pixi "
                            "run "
                            "--manifest-path "
                            "~s25idcuser/src/oaty-bar "
                            "fit-fluorescence "
                            "4ddd5c94-0825-4ab8-b1b5-12e8e5d66a48 "
                            "--raw-profile "
                            "oaty-bar "
                            "--results-profile "
                            "oaty-bar-results"
                        ),
                        "endTime": 1778850775.6094248,
                        "exitStatus": 0,
                        "runTime": 9.560480117797852,
                        "stageId": "020-FIT_FLUORESCENCE",
                        "startTime": 1778850766.0489447,
                        "status": "done",
                        "stdErr": (
                            "WARNING "
                            "[2026-05-15 "
                            "08:12:54]: "
                            "Fitting "
                            "0 "
                            "chemical "
                            "elements "
                            "for "
                            "run "
                            "'http://s25idcdm.xray.aps.anl.gov:8020/api/v1/metadata/raw/4ddd5c94-0825-4ab8-b1b5-12e8e5d66a48'\n"
                            "WARNING "
                            "[2026-05-15 "
                            "08:12:54]: "
                            "Fitting "
                            "produced "
                            "no "
                            "results.\n"
                        ),
                        "stdOut": "",
                        "submitTime": 1778850766.0481126,
                        "userAccount": "s25idcuser",
                        "workingDir": None,
                    }
                },
                "command": (
                    "/APSshare/bin/pixi "
                    "run "
                    "--manifest-path "
                    "~s25idcuser/src/oaty-bar "
                    "fit-fluorescence "
                    "$run_uid "
                    "--raw-profile "
                    "oaty-bar "
                    "--results-profile "
                    "oaty-bar-results"
                ),
                "nCompletedChildProcesses": 1,
                "nQueuedChildProcesses": 0,
                "nRunningChildProcesses": 0,
            },
            "030-EXPORT": {
                "childProcesses": {
                    "2": {
                        "childProcessNumber": 2,
                        "command": (
                            "/usr/bin/sudo "
                            "-u "
                            "s25idcuser "
                            "-- "
                            "/APSshare/bin/pixi "
                            "run "
                            "--manifest-path "
                            "~s25idcuser/src/oaty-bar "
                            "export-hdf "
                            "4ddd5c94-0825-4ab8-b1b5-12e8e5d66a48 "
                            "/gdata/dm/25IDC/commissioning-2026-C2 "
                            "--raw-profile "
                            "oaty-bar "
                            "--results-profile "
                            "oaty-bar-results"
                        ),
                        "endTime": 1778850780.449093,
                        "exitStatus": 1,
                        "runTime": 4.834179162979126,
                        "stageId": "030-EXPORT",
                        "startTime": 1778850775.614914,
                        "status": "failed",
                        "stdErr": (
                            "Traceback "
                            "(most "
                            "recent "
                            "call "
                            "last):\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/.pixi/envs/default/bin/export-hdf", '
                            "line "
                            "10, "
                            "in "
                            "<module>\n"
                            "    "
                            "sys.exit(main())\n"
                            "             "
                            "~~~~^^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/src/oaty_bar/_export_hdf.py", '
                            "line "
                            "497, "
                            "in "
                            "main\n"
                            "    "
                            "export_hdf(\n"
                            "    "
                            "~~~~~~~~~~^\n"
                            "        "
                            "uid=parsed.uid,\n"
                            "        "
                            "^^^^^^^^^^^^^^^\n"
                            "    "
                            "...<2 "
                            "lines>...\n"
                            "        "
                            "results_profile=parsed.results_profile,\n"
                            "        "
                            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
                            "    "
                            ")\n"
                            "    "
                            "^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/src/oaty_bar/_export_hdf.py", '
                            "line "
                            "474, "
                            "in "
                            "export_hdf\n"
                            "    "
                            "asyncio.run(serialize_hdf(buff=target_file, "
                            "run=run, "
                            "results_runs=results_runs))\n"
                            "    "
                            "~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/.pixi/envs/default/lib/python3.14/asyncio/runners.py", '
                            "line "
                            "204, "
                            "in "
                            "run\n"
                            "    "
                            "return "
                            "runner.run(main)\n"
                            "           "
                            "~~~~~~~~~~^^^^^^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/.pixi/envs/default/lib/python3.14/asyncio/runners.py", '
                            "line "
                            "127, "
                            "in "
                            "run\n"
                            "    "
                            "return "
                            "self._loop.run_until_complete(task)\n"
                            "           "
                            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/.pixi/envs/default/lib/python3.14/asyncio/base_events.py", '
                            "line "
                            "719, "
                            "in "
                            "run_until_complete\n"
                            "    "
                            "return "
                            "future.result()\n"
                            "           "
                            "~~~~~~~~~~~~~^^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/src/oaty_bar/_export_hdf.py", '
                            "line "
                            "431, "
                            "in "
                            "serialize_hdf\n"
                            "    "
                            "with "
                            "h5py.File(buff, "
                            'mode="w") '
                            "as "
                            "nxfile:\n"
                            "         "
                            "~~~~~~~~~^^^^^^^^^^^^^^^^\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/.pixi/envs/default/lib/python3.14/site-packages/h5py/_hl/files.py", '
                            "line "
                            "555, "
                            "in "
                            "__init__\n"
                            "    "
                            "fid "
                            "= "
                            "make_fid(name, "
                            "mode, "
                            "userblock_size, "
                            "fapl, "
                            "fcpl, "
                            "swmr=swmr)\n"
                            "  "
                            "File "
                            '"/home/beams0/S25IDCUSER/src/oaty-bar/.pixi/envs/default/lib/python3.14/site-packages/h5py/_hl/files.py", '
                            "line "
                            "238, "
                            "in "
                            "make_fid\n"
                            "    "
                            "fid "
                            "= "
                            "h5f.create(name, "
                            "h5f.ACC_TRUNC, "
                            "fapl=fapl, "
                            "fcpl=fcpl)\n"
                            "  "
                            "File "
                            '"h5py/_objects.pyx", '
                            "line "
                            "54, "
                            "in "
                            "h5py._objects.with_phil.wrapper\n"
                            "  "
                            "File "
                            '"h5py/_objects.pyx", '
                            "line "
                            "55, "
                            "in "
                            "h5py._objects.with_phil.wrapper\n"
                            "  "
                            "File "
                            '"h5py/h5f.pyx", '
                            "line "
                            "126, "
                            "in "
                            "h5py.h5f.create\n"
                            "PermissionError: "
                            "[Errno "
                            "13] "
                            "Unable "
                            "to "
                            "synchronously "
                            "create "
                            "file "
                            "(unable "
                            "to "
                            "open "
                            "file: "
                            "name "
                            "= "
                            "'/gdata/dm/25IDC/commissioning-2026-C2/202605142107-count-4ddd5c94.h5', "
                            "errno "
                            "= "
                            "13, "
                            "error "
                            "message "
                            "= "
                            "'Permission "
                            "denied', "
                            "flags "
                            "= "
                            "13, "
                            "o_flags "
                            "= "
                            "242)\n"
                        ),
                        "stdOut": "",
                        "submitTime": 1778850775.6113808,
                        "userAccount": "s25idcuser",
                        "workingDir": None,
                    }
                },
                "command": (
                    "/APSshare/bin/pixi run "
                    "--manifest-path "
                    "~s25idcuser/src/oaty-bar "
                    "export-hdf $run_uid "
                    "$target_folder "
                    "--raw-profile oaty-bar "
                    "--results-profile "
                    "oaty-bar-results"
                ),
                "nFailedChildProcesses": 1,
                "nQueuedChildProcesses": 0,
                "nRunningChildProcesses": 0,
            },
        },
        "userAccount": "s25idcuser",
        "version": 1,
    },
}


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
    print(new_workflow)
    url = httpx.URL(
        f"{base_uri}/dm/workflows/addWorkflow",
        params={
            "allowCurrentUsername": 0,
            "workflow": (
                "b'ZXlKdVlXMWxJam9pWlhoaGJYQnNaUzB3TVNJc0ltOTNibVZ5SWpvaVpIVnRiWGxmZFhObGNpSXNJblZ6WlhKQlkyTnZkVzUwSWpvaVpIVnRiWGxmZFhObGNpSXNJbVJsYzJOeWFYQjBhVzl1SWpvaVYyOXlhMlpzYjNjZ1JYaGhiWEJzWlNBd01TSXNJbWxrSWpvaU5qbG1NR013WWpFME5EQTVZakZoTnpReE9EVTBZbVUySWl3aWMzUmhaMlZ6SWpwN0lqQXhMVk5VUVZKVUlqcDdJbU52YlcxaGJtUWlPaUl2WW1sdUwyUmhkR1VnS3lWWkpXMGxaQ1ZJSlUwbFV5SXNJbTkxZEhCMWRGWmhjbWxoWW14bFVtVm5aWGhNYVhOMElqcGJJaWcvVUR4MGFXMWxVM1JoYlhBK0xpb3BJbDE5TENJd01pMU5TMFJKVWlJNmV5SmpiMjF0WVc1a0lqb2lMMkpwYmk5dGEyUnBjaUF0Y0NBdmRHMXdMM2R2Y210bWJHOTNMaVIwYVcxbFUzUmhiWEFpTENKdmRYUndkWFJXWVhKcFlXSnNaVkpsWjJWNFRHbHpkQ0k2VzExOUxDSXdNeTFGUTBoUElqcDdJbU52YlcxaGJtUWlPaUl2WW1sdUwyVmphRzhnWEZ4Y0lsTlVRVkpVSUVwUFFpQkpSRG9nSkdsa1hGeGNJaUErSUM5MGJYQXZkMjl5YTJac2IzY3VKSFJwYldWVGRHRnRjQzhrYVdRdWIzVjBJaXdpYjNWMGNIVjBWbUZ5YVdGaWJHVlNaV2RsZUV4cGMzUWlPbHRkZlN3aU1EUXRUVVExVTFWTklqcDdJbU52YlcxaGJtUWlPaUl2WW1sdUwyMWtOWE4xYlNBa1ptbHNaVkJoZEdnZ2ZDQmpkWFFnTFdZeElDMWtYRnhjSWlCY1hGd2lJaXdpYjNWMGNIVjBWbUZ5YVdGaWJHVlNaV2RsZUV4cGMzUWlPbHNpS0Q5UVBHMWtOVk4xYlQ0dUtpa2lYWDBzSWpBMUxVVkRTRThpT25zaVkyOXRiV0Z1WkNJNkltVmphRzhnWEZ4Y0lrWkpURVVnSkdacGJHVlFZWFJvSUUxRU5TQlRWVTA2SUNSdFpEVlRkVzFjWEZ3aUlENCtJQzkwYlhBdmQyOXlhMlpzYjNjdUpIUnBiV1ZUZEdGdGNDOGthV1F1YjNWMElpd2liM1YwY0hWMFZtRnlhV0ZpYkdWU1pXZGxlRXhwYzNRaU9sdGRmU3dpTURZdFJFOU9SU0k2ZXlKamIyMXRZVzVrSWpvaUwySnBiaTlsWTJodklGeGNYQ0pUVkU5UUlFcFBRaUJKUkRvZ0pHbGtYRnhjSWlBK1BpQXZkRzF3TDNkdmNtdG1iRzkzTGlSMGFXMWxVM1JoYlhBdkpHbGtMbTkxZENJc0ltOTFkSEIxZEZaaGNtbGhZbXhsVW1WblpYaE1hWE4wSWpwYlhYMTlmUT09'"
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
async def test_set_workflow(httpx_mock, api):
    new_workflow = Workflow(**workflows[0])
    # Mock for retrieving the existing workflow
    url = httpx.URL(
        f"{base_uri}/dm/workflows/updateWorkflow",
        params={
            "allowCurrentUsername": 0,
            "workflow": (
                "b'ZXlKdVlXMWxJam9pWlhoaGJYQnNaUzB3TVNJc0ltOTNibVZ5SWpvaVpIVnRiWGxmZFhObGNpSXNJblZ6WlhKQlkyTnZkVzUwSWpvaVpIVnRiWGxmZFhObGNpSXNJbVJsYzJOeWFYQjBhVzl1SWpvaVYyOXlhMlpzYjNjZ1JYaGhiWEJzWlNBd01TSXNJbWxrSWpvaU5qbG1NR013WWpFME5EQTVZakZoTnpReE9EVTBZbVUySWl3aWMzUmhaMlZ6SWpwN0lqQXhMVk5VUVZKVUlqcDdJbU52YlcxaGJtUWlPaUl2WW1sdUwyUmhkR1VnS3lWWkpXMGxaQ1ZJSlUwbFV5SXNJbTkxZEhCMWRGWmhjbWxoWW14bFVtVm5aWGhNYVhOMElqcGJJaWcvVUR4MGFXMWxVM1JoYlhBK0xpb3BJbDE5TENJd01pMU5TMFJKVWlJNmV5SmpiMjF0WVc1a0lqb2lMMkpwYmk5dGEyUnBjaUF0Y0NBdmRHMXdMM2R2Y210bWJHOTNMaVIwYVcxbFUzUmhiWEFpTENKdmRYUndkWFJXWVhKcFlXSnNaVkpsWjJWNFRHbHpkQ0k2VzExOUxDSXdNeTFGUTBoUElqcDdJbU52YlcxaGJtUWlPaUl2WW1sdUwyVmphRzhnWEZ4Y0lsTlVRVkpVSUVwUFFpQkpSRG9nSkdsa1hGeGNJaUErSUM5MGJYQXZkMjl5YTJac2IzY3VKSFJwYldWVGRHRnRjQzhrYVdRdWIzVjBJaXdpYjNWMGNIVjBWbUZ5YVdGaWJHVlNaV2RsZUV4cGMzUWlPbHRkZlN3aU1EUXRUVVExVTFWTklqcDdJbU52YlcxaGJtUWlPaUl2WW1sdUwyMWtOWE4xYlNBa1ptbHNaVkJoZEdnZ2ZDQmpkWFFnTFdZeElDMWtYRnhjSWlCY1hGd2lJaXdpYjNWMGNIVjBWbUZ5YVdGaWJHVlNaV2RsZUV4cGMzUWlPbHNpS0Q5UVBHMWtOVk4xYlQ0dUtpa2lYWDBzSWpBMUxVVkRTRThpT25zaVkyOXRiV0Z1WkNJNkltVmphRzhnWEZ4Y0lrWkpURVVnSkdacGJHVlFZWFJvSUUxRU5TQlRWVTA2SUNSdFpEVlRkVzFjWEZ3aUlENCtJQzkwYlhBdmQyOXlhMlpzYjNjdUpIUnBiV1ZUZEdGdGNDOGthV1F1YjNWMElpd2liM1YwY0hWMFZtRnlhV0ZpYkdWU1pXZGxlRXhwYzNRaU9sdGRmU3dpTURZdFJFOU9SU0k2ZXlKamIyMXRZVzVrSWpvaUwySnBiaTlsWTJodklGeGNYQ0pUVkU5UUlFcFBRaUJKUkRvZ0pHbGtYRnhjSWlBK1BpQXZkRzF3TDNkdmNtdG1iRzkzTGlSMGFXMWxVM1JoYlhBdkpHbGtMbTkxZENJc0ltOTFkSEIxZEZaaGNtbGhZbXhsVW1WblpYaE1hWE4wSWpwYlhYMTlmUT09'"
            ),
        },
    )
    httpx_mock.add_response(url=url, method="PUT", json=workflows[0])
    await maybe_await(api.set_workflow(name="example-01", workflow=new_workflow))


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
                "b'ZXlKdVlXMWxJam9pWlhoaGJYQnNaUzB3TVNJc0ltOTNibVZ5SWpvaVpIVnRiWGxmZFhObGNpSXNJblZ6WlhKQlkyTnZkVzUwSWpvaVpIVnRiWGxmZFhObGNpSXNJbVJsYzJOeWFYQjBhVzl1SWpvaVlTQmlaWFIwWlhJZ1pHVnpZM0pwY0hScGIyNGlMQ0pwWkNJNklqWTVaakJqTUdJeE5EUXdPV0l4WVRjME1UZzFOR0psTmlJc0luTjBZV2RsY3lJNmV5SXdNUzFUVkVGU1ZDSTZleUpqYjIxdFlXNWtJam9pTDJKcGJpOWtZWFJsSUNzbFdTVnRKV1FsU0NWTkpWTWlMQ0p2ZFhSd2RYUldZWEpwWVdKc1pWSmxaMlY0VEdsemRDSTZXeUlvUDFBOGRHbHRaVk4wWVcxd1BpNHFLU0pkZlN3aU1ESXRUVXRFU1ZJaU9uc2lZMjl0YldGdVpDSTZJaTlpYVc0dmJXdGthWElnTFhBZ0wzUnRjQzkzYjNKclpteHZkeTRrZEdsdFpWTjBZVzF3SWl3aWIzVjBjSFYwVm1GeWFXRmliR1ZTWldkbGVFeHBjM1FpT2x0ZGZTd2lNRE10UlVOSVR5STZleUpqYjIxdFlXNWtJam9pTDJKcGJpOWxZMmh2SUZ4Y1hDSlRWRUZTVkNCS1QwSWdTVVE2SUNScFpGeGNYQ0lnUGlBdmRHMXdMM2R2Y210bWJHOTNMaVIwYVcxbFUzUmhiWEF2Skdsa0xtOTFkQ0lzSW05MWRIQjFkRlpoY21saFlteGxVbVZuWlhoTWFYTjBJanBiWFgwc0lqQTBMVTFFTlZOVlRTSTZleUpqYjIxdFlXNWtJam9pTDJKcGJpOXRaRFZ6ZFcwZ0pHWnBiR1ZRWVhSb0lId2dZM1YwSUMxbU1TQXRaRnhjWENJZ1hGeGNJaUlzSW05MWRIQjFkRlpoY21saFlteGxVbVZuWlhoTWFYTjBJanBiSWlnL1VEeHRaRFZUZFcwK0xpb3BJbDE5TENJd05TMUZRMGhQSWpwN0ltTnZiVzFoYm1RaU9pSmxZMmh2SUZ4Y1hDSkdTVXhGSUNSbWFXeGxVR0YwYUNCTlJEVWdVMVZOT2lBa2JXUTFVM1Z0WEZ4Y0lpQStQaUF2ZEcxd0wzZHZjbXRtYkc5M0xpUjBhVzFsVTNSaGJYQXZKR2xrTG05MWRDSXNJbTkxZEhCMWRGWmhjbWxoWW14bFVtVm5aWGhNYVhOMElqcGJYWDBzSWpBMkxVUlBUa1VpT25zaVkyOXRiV0Z1WkNJNklpOWlhVzR2WldOb2J5QmNYRndpVTFSUFVDQktUMElnU1VRNklDUnBaRnhjWENJZ1BqNGdMM1J0Y0M5M2IzSnJabXh2ZHk0a2RHbHRaVk4wWVcxd0x5UnBaQzV2ZFhRaUxDSnZkWFJ3ZFhSV1lYSnBZV0pzWlZKbFoyVjRUR2x6ZENJNlcxMTlmWDA9'"
            ),
        },
    )
    httpx_mock.add_response(url=url, method="PUT", json=workflows[0])
    update = {"description": "a better description"}
    await maybe_await(api.update_workflow(name="example-01", update=update))


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_get_processing_job(httpx_mock, api):
    url = httpx.URL(
        f"{base_uri}/dm/processingJobsByOwner/dummy_user/{failed_job['id']}",
    )
    httpx_mock.add_response(url=url, json=failed_job)
    job0 = await maybe_await(
        api.processing_job(id="7e01fb97-44b1-4b7f-b1ca-d08624eb8c77")
    )
    assert job0.file_count == 1
    assert job0.end.year == 2026
    assert job0.error_message == ""
    assert job0.id == "7e01fb97-44b1-4b7f-b1ca-d08624eb8c77"
    assert job0.workflow.name == "simple"
    assert job0.workflow.stages["030-EXPORT"].child_processes["2"].status == "failed"
    assert (
        "Traceback"
        in job0.workflow.stages["030-EXPORT"].child_processes["2"].standard_error
    )


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
