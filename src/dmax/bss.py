"""
REST API Endpoints
==================

- /dm/esaf/stationEsafs/{station_name*}/{beamline_name*}?year={year}
- /dm/esaf/stationEsafsById/{station_name*}/{esaf_id}
- /dm/bss/stationProposals/{station_name*}/{beamline_name*}?runName={run}
- /dm/bss/stationProposalsById/{station_name*}/{proposal_id}?runName={run}

* double base64 encoded bytestring
"""

import datetime as dt
import json
from base64 import b64encode
from collections.abc import Generator
from typing import Any, Mapping

import httpx
from pydantic import BaseModel

__all__ = ["Esaf", "Proposal", "User"]


class User(BaseModel):
    badge: str
    first_name: str
    last_name: str
    email: str | None
    is_pi: bool
    institution: str | None


class Esaf(BaseModel):
    esaf_id: str
    description: str
    sector: str
    title: str
    start: dt.datetime
    end: dt.datetime
    status: str
    users: list[User]


class Proposal(BaseModel):
    title: str
    proposal_id: str
    users: list[User]
    start: dt.datetime
    end: dt.datetime
    duration: dt.timedelta
    mail_in: bool
    proprietary: bool


def encode(string: str) -> bytes:
    """Double-base64 encoded version of the input *string*."""
    return b64encode(b64encode(string.encode()))


def _to_proposal(data: Mapping[str, Any]) -> Proposal:
    # Scheduling dates
    # dt_format = "%Y-%m-%d %H:%M:%S"
    start = dt.datetime.fromisoformat(data["startTime"])
    end = dt.datetime.fromisoformat(data["endTime"])
    duration = dt.timedelta(seconds=data["duration"])
    # Create users for the proposal
    users = [
        User(
            badge=user_data["badge"],
            first_name=user_data["firstName"],
            last_name=user_data["lastName"],
            is_pi=user_data["piFlag"],
            email="",
            institution=user_data["institution"],
        )
        for user_data in data["experimenters"]
    ]
    # Create the proposal itself
    return Proposal(
        title=data["title"],
        proposal_id=f"{data['id']:07}",
        users=users,
        start=start,
        end=end,
        duration=duration,
        mail_in=(data["mailInFlag"] == "Yes"),
        proprietary=(data["proprietaryFlag"] == "Yes"),
    )


def request_proposals(beamline: str, cycle: str | None, station_name: str, context):
    """Load the proposals for a given *beamline* during a given *cycle*."""
    url = f"bss/stationProposals/{encode(station_name)!r}/{encode(beamline)!r}"
    params = {"runName": cycle} if cycle else None
    json_data = yield context.get(url, params=params)
    # response = yield context.get(url, params=params)
    data = json.loads(json_data)
    return [_to_proposal(datum) for datum in data]


def request_proposal(proposal_id: str, cycle: str | None, station_name: str, context):
    """Load the given proposal on a given *beamline* during a given *cycle*."""
    url = f"bss/stationProposalsById/{encode(station_name)!r}/{proposal_id}"
    params = {"runName": cycle} if cycle else None
    json_data = yield context.get(url, params=params)
    data = json.loads(json_data)
    return _to_proposal(data)


def _to_esaf(data: Mapping[str, Any]) -> Esaf:
    # Scheduling dates
    dt_format = "%Y-%m-%d %H:%M:%S"
    start = dt.datetime.strptime(data["experimentStartDate"], dt_format)
    end = dt.datetime.strptime(data["experimentEndDate"], dt_format)
    # Users
    users = [
        User(
            badge=user["badge"],
            first_name=user["firstName"],
            last_name=user["lastName"],
            email=user.get("email"),
            is_pi=user["piFlag"] == "Yes",
            institution=None,
        )
        for user in data["experimentUsers"]
    ]
    # Create the ESAF
    return Esaf(
        title=data["esafTitle"],
        description=data["description"],
        esaf_id=str(data["esafId"]),
        sector=data["sector"],
        status=data["esafStatus"],
        start=start,
        end=end,
        users=users,
    )


def request_esaf(
    esaf_id: str, station_name: str, context
) -> Generator[httpx.Request, str, Esaf]:
    url = f"esaf/stationEsafsById/{encode(station_name)!r}/{esaf_id}"
    json_data = yield context.get(url)
    return _to_esaf(json.loads(json_data))


def request_esafs(
    beamline: str, year: str | None, station_name: str, context
) -> Generator[httpx.Request, str, list[Esaf]]:
    """Load the ESAF's for the given *beamline* and *year*."""
    url = f"esaf/stationEsafs/{encode(station_name)!r}/{encode(beamline)!r}"
    params = {"year": year} if year else None
    json_data = yield context.get(url, params=params)
    data = json.loads(json_data)
    esafs_ = [_to_esaf(datum) for datum in data]
    return esafs_


# -----------------------------------------------------------------------------
# :author:    Mark Wolfman
# :email:     wolfman@anl.gov
# :copyright: Copyright © 2025, UChicago Argonne, LLC
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
