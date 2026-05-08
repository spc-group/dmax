import datetime as dt

import httpx
import pytest
import stamina

from dmax import AsyncClient, Client
from dmax.testing import maybe_await

experiments = [
    {
        "name": "fong-25idc-2026-C1",
        "description": "HERFD-XAS Investigation of Strain-Tuned Ni-O Orbital Hybridization in Nickelate Films",
        "id": 26356,
        "primaryStorage": {
            "description": "APS SOJOURNER Storage",
            "name": "SOJOURNER",
            "id": 5,
        },
        "experimentStation": {
            "name": "25IDC",
            "id": 70,
            "description": "Station for 25-ID-C",
        },
        "experimentType": {"name": "25IDC", "description": "Type for 25IDC", "id": 89},
        "createDate": "2026-02-26 13:26:39.763553-06:00",
        "updateDate": "2026-02-26 13:26:39.763553-06:00",
        "startDate": "2026-02-13 00:00:00-06:00",
        "endDate": "2026-02-16 00:00:00-06:00",
        "experimentTypeId": 89,
        "experimentStationId": 70,
        "primaryStorageId": 5,
        "authGroupName": "fong25idc2-25idc-e58804",
    },
    {
        "name": "chen_2026-2",
        "description": "Ultrafast X-ray Absorption Spectroscopy Investigation of Surface Charge Storage Mechanisms in Ni(OH)",
        "id": 27200,
        "primaryStorage": {
            "description": "APS SOJOURNER Storage",
            "name": "SOJOURNER",
            "id": 5,
        },
        "experimentStation": {
            "name": "25IDC",
            "id": 70,
            "description": "Station for 25-ID-C",
        },
        "experimentType": {"name": "25IDC", "description": "Type for 25IDC", "id": 89},
        "createDate": "2026-04-24 14:44:05.023298-05:00",
        "updateDate": "2026-04-24 14:44:05.023298-05:00",
        "startDate": "2026-04-20 00:00:00-05:00",
        "endDate": "2026-04-22 00:00:00-05:00",
        "experimentTypeId": 89,
        "experimentStationId": 70,
        "rootPath": "chen_2026-2",
        "primaryStorageId": 5,
        "authGroupName": "chen20262-25idc-f69435",
    },
]

base_uri = "http://localhost:12345"


@pytest.fixture()
def api(request):
    stamina.set_testing(True)
    if getattr(request, "param", "async") == "async":
        client = AsyncClient(
            username="", password="", station_name="25IDC", data_storage_uri=base_uri
        )
    else:
        client = Client(
            username="", password="", station_name="25IDC", data_storage_uri=base_uri
        )
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["sync", "async"], indirect=True)
async def test_get_experiments(httpx_mock, api):
    # https://xraydtn03.xray.aps.anl.gov:22237/dm/experimentsByStation/25IDC
    url = httpx.URL(
        f"{base_uri}/dm/experimentsByStation/25IDC",
    )
    httpx_mock.add_response(url=url, json=experiments)
    experiments_ = await maybe_await(api.experiments())
    assert len(experiments_) == 2
    exp0, exp1 = experiments_
    assert exp0.name == "fong-25idc-2026-C1"
    assert (
        exp0.description
        == "HERFD-XAS Investigation of Strain-Tuned Ni-O Orbital Hybridization in Nickelate Films"
    )
    assert exp0.id == 26356
    assert exp0.created == dt.datetime(
        2026, 2, 26, 13, 26, 39, 763553, tzinfo=dt.timezone(dt.timedelta(hours=-6))
    )
    assert exp0.station.description == "Station for 25-ID-C"


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
