# b'ZEdWMGNtRnRiUzEwWlhOMGFXNW5MVEl3TWpZdFF6ST0K' => b'tetramm-testing-2026-C2'
# b'TDI1bGRDOXpNalZrWVhSaEwyVjRjRzl5ZEM4eU5TMUpSQzFETDNSbGRISmhiVzB0ZEdWemRHbHVaeTB5TURJMkxVTXkK' => b'/net/s25data/export/25-ID-C/tetramm-testing-2026-C2'
# taskInfo=b'ZTMwPQo=' => {}

# sm.host='https://s25idcdm.xray.aps.anl.gov:33336'
# url="/dm/experimentsByName/b'ZEdWMGNtRnRiUzEwWlhOMGFXNW5MVEl3TWpZdFF6ST0K'/startDaq/b'TDI1bGRDOXpNalZrWVhSaEwyVjRjRzl5ZEM4eU5TMUpSQzFETDNSbGRISmhiVzB0ZEdWemRHbHVaeTB5TURJMkxVTXkK'?taskInfo=b'ZTMwPQo='"
# 'data={}'
# method='POST'
# contentType='html'
# id=2251bce7-a8d4-40ad-b685-57be42e24d32 experimentName=tetramm-testing-2026-C2 dataDirectory=/net/s25data/export/25-ID-C/tetramm-testing-2026-C2 status=running nProcessedFiles=0 nProcessingErrors=0 countFiles=0 startTime=1780114297.2845373 startTimestamp=2026/05/29 23:11:37 CDT


from base64 import b64encode

import httpx
import pytest
import stamina

from dmax import AsyncClient, Client
from dmax.testing import maybe_await

daq_response = {
    "countFiles": 0,
    "dataDirectory": "/net/s25data/export/25-ID-C/tetramm-testing-2026-C2",
    "experimentName": "tetramm-testing-2026-C2",
    "experimentStationName": "25IDC",
    "id": "2251bce7-a8d4-40ad-b685-57be42e24d32",
    "nProcessedFiles": 0,
    "nProcessingErrors": 0,
    "startTime": 1780114297.2845373,
    "startTimestamp": "2026/05/29 23:11:37 CDT",
    "status": "running",
    "storageDirectory": "/gdata/dm/25IDC/tetramm-testing-2026-C2/data",
    "storageHost": "xraydtn03.xray.aps.anl.gov",
    "storageUrl": (
        "sojourner://xraydtn03.xray.aps.anl.gov/gdata/dm/25IDC/tetramm-testing-2026-C2"
    ),
    "workflowJobOwner": "s25idcuser",
}

base_uri = "http://localhost:12345"


@pytest.fixture()
def api(request):
    stamina.set_testing(True)
    if getattr(request, "param", "async") == "async":
        client = AsyncClient(
            username="", password="", station_name="25IDC", data_archive_uri=base_uri
        )
    else:
        client = Client(
            username="", password="", station_name="25IDC", data_archive_uri=base_uri
        )
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_start_data_archive_queue(httpx_mock, api):
    # url="/dm/experimentsByName/b'ZEdWMGNtRnRiUzEwWlhOMGFXNW5MVEl3TWpZdFF6ST0K'/startDaq/b'TDI1bGRDOXpNalZrWVhSaEwyVjRjRzl5ZEM4eU5TMUpSQzFETDNSbGRISmhiVzB0ZEdWemRHbHVaeTB5TURJMkxVTXkK'?taskInfo=b'ZTMwPQo='"
    dm_exp_b64 = b64encode(b64encode(b"tetramm-testing-2026-C2"))
    src_b64 = b64encode(
        b64encode(b"/net/s25data/export/25-ID-C/tetramm-testing-2026-C2")
    )
    task_info_b64 = b64encode(b64encode(b"{}"))
    url = httpx.URL(
        f"{base_uri}/dm/experimentsByName/{dm_exp_b64!r}/startDaq/{src_b64!r}?taskInfo={task_info_b64!r}",
    )
    httpx_mock.add_response(url=url, method="POST", json=daq_response)
    daq_ = await maybe_await(
        api.start_data_archive_queue(
            experiment_name="tetramm-testing-2026-C2",
            source_directory="/net/s25data/export/25-ID-C/tetramm-testing-2026-C2",
        )
    )
    assert daq_.file_count == 0
    assert daq_.data_directory == "/net/s25data/export/25-ID-C/tetramm-testing-2026-C2"
    assert daq_.experiment_name == "tetramm-testing-2026-C2"
    assert daq_.station_name == "25IDC"
    assert daq_.id == "2251bce7-a8d4-40ad-b685-57be42e24d32"
    assert daq_.processed_file_count == 0
    assert daq_.processing_errors_count == 0
    assert daq_.start == 1780114297.2845373
    assert daq_.status == "running"
    assert daq_.storage_directory == "/gdata/dm/25IDC/tetramm-testing-2026-C2/data"
    assert daq_.storage_host == "xraydtn03.xray.aps.anl.gov"
    assert (
        daq_.storage_url
        == "sojourner://xraydtn03.xray.aps.anl.gov/gdata/dm/25IDC/tetramm-testing-2026-C2"
    )
    assert daq_.workflow_job_owner == "s25idcuser"


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_skip_file_path(httpx_mock, api):
    # ?taskInfo=b'ZXlKemEybHdSbWxzWlZCaGRHaFFZWFIwWlhKdUlqb2dJaTV3YVhocEx5b2lmUT09Cg=='
    dm_exp_b64 = b64encode(b64encode(b"tetramm-testing-2026-C2"))
    src_b64 = b64encode(
        b64encode(b"/net/s25data/export/25-ID-C/tetramm-testing-2026-C2")
    )
    task_info_b64 = b64encode(b64encode(b'{"skipFilePathPattern": ".pixi/*"}'))
    url = httpx.URL(
        f"{base_uri}/dm/experimentsByName/{dm_exp_b64!r}/startDaq/{src_b64!r}?taskInfo={task_info_b64!r}",
    )
    httpx_mock.add_response(url=url, method="POST", json=daq_response)
    daq_ = await maybe_await(
        api.start_data_archive_queue(
            experiment_name="tetramm-testing-2026-C2",
            source_directory="/net/s25data/export/25-ID-C/tetramm-testing-2026-C2",
            skip=".pixi/*",
        )
    )
    assert daq_.file_count == 0
    assert daq_.data_directory == "/net/s25data/export/25-ID-C/tetramm-testing-2026-C2"
    assert daq_.experiment_name == "tetramm-testing-2026-C2"
    assert daq_.station_name == "25IDC"
    assert daq_.id == "2251bce7-a8d4-40ad-b685-57be42e24d32"
    assert daq_.processed_file_count == 0
    assert daq_.processing_errors_count == 0
    assert daq_.start == 1780114297.2845373
    assert daq_.status == "running"
    assert daq_.storage_directory == "/gdata/dm/25IDC/tetramm-testing-2026-C2/data"
    assert daq_.storage_host == "xraydtn03.xray.aps.anl.gov"
    assert (
        daq_.storage_url
        == "sojourner://xraydtn03.xray.aps.anl.gov/gdata/dm/25IDC/tetramm-testing-2026-C2"
    )
    assert daq_.workflow_job_owner == "s25idcuser"


# -----------------------------------------------------------------------------
# :author:    Mark Wolfman
# :email:     wolfman@anl.gov
# :copyright: Copyright © 2026, UChicago Argonne, LLC
#
# Distributed under the terms of the 3-Clause BSD License
#
# The full license is in the file LICENSE, distributed with this software.
#
# DISCLAIMER
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# -----------------------------------------------------------------------------
