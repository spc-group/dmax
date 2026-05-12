import os

import httpx

from . import data_storage as ds
from . import processing, scheduling
from .context import AsyncContext, SyncContext


def raise_for_status(response: httpx.Response) -> httpx.Response:
    """Raises an exception if the response did not complete successfully.

    Similar to the behavior of httpx.Response.raise_for_status, but
    also accounts for situations where the dm API returns a 200 status
    code, but the response content contains error information.

    """
    response = response.raise_for_status()
    content = response.json()
    if "errorCode" not in content:
        # Everything is fine, just send the response on
        return response
    error_code = content.get("errorCode", "??")
    error_message = content.get("errorMessage", "Unknown error")
    raise httpx.HTTPStatusError(
        f"{error_message} ({error_code})", response=response, request=response.request
    )


def standardize_uri(uri):
    """Remove trailing characters, etc so we all agree on URI structure."""
    uri = uri.rstrip("/")
    if uri.split("/")[-1] != "dm":
        # Add the 'dm' prefix for paths
        uri = f"{uri}/dm"
    return uri


def uri_or_default(uri: str, env_variable: str, default: str):
    """Return a DM URI, either explicitly, from environmental variables,
    or a default.

    Parameters
    ==========
    uri
      The user-provided URI. Could be an empty string.
    env_variable
      The name of the environmental variable to check if an explicit
      URI is not given.
    default
      A fallback URI to use if neither *uri* is given nor
      *env_variable* is set.

    """
    new_uri = uri or os.environ.get(env_variable, default)
    return standardize_uri(new_uri)


class Client:
    username: str
    password: str
    station_name: str
    Context: type

    def __init__(
        self,
        *,
        username: str = "",
        password: str = "",
        station_name: str = "",
        scheduling_uri: str = "",
        data_storage_uri: str = "",
        processing_uri: str = "",
    ):
        """*username*, *password*, and *station_name* are all assigned by the
        data management group.

        """
        self.station_name = station_name or os.environ.get("DM_STATION_NAME", "")
        # Login credentials might be stored in a file on disk
        login_file = os.environ.get("DM_LOGIN_FILE", "")
        if login_file:
            with open(login_file, mode="r") as login_fd:
                username_, password_ = login_fd.readline().strip().split("|")
            self.username = username or username_
            self.password = password or password_
        else:
            self.username = username
            self.password = password
        # There are multiple API's we need, so use multiple contexts
        vm_host = (
            f"https://s{self.station_name.lower()}dm.xray.aps.anl.gov"
            if self.station_name != ""
            else "http://localhost"
        )
        uri = uri_or_default(
            uri=scheduling_uri,
            env_variable="DM_APS_DB_WEB_SERVICE_URL",
            default="https://xraydtn03.xray.aps.anl.gov:11337",
        )
        self._bss_context = self.Context(
            base_uri=uri, username=self.username, password=self.password
        )

        uri = uri_or_default(
            uri=data_storage_uri,
            env_variable="DM_DS_WEB_SERVICE_URL",
            default=f"{vm_host}:22237",
        )
        self._ds_context = self.Context(
            base_uri=uri, username=self.username, password=self.password
        )

        uri = uri_or_default(
            uri=processing_uri,
            env_variable="DM_PROC_WEB_SERVICE_URL",
            default="{vm_host}:55536",
        )
        self._proc_context = self.Context(
            base_uri=uri, username=self.username, password=self.password
        )


class AsyncClient(Client):
    """Client for the APS data management REST API."""

    Context = AsyncContext

    async def serve_requests(self, requests):
        # Do the requests one at a time
        response = None
        return_value = None
        while True:
            try:
                request = requests.send(response)
            except StopIteration as exc:
                return_value = exc.value
                break
            response = await request.http_client.send(request.http_request)
            response = raise_for_status(response).text
        return return_value

    async def esafs(
        self, beamline: str = "", year: str | None = None
    ) -> list[scheduling.Esaf]:
        """Load the ESAF's for the given *beamline* and *year*."""
        requests = scheduling.request_esafs(
            beamline=beamline,
            year=year,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return await self.serve_requests(requests)

    async def esaf(self, esaf_id: str) -> scheduling.Esaf:
        """Load the ESAF's for the given *sector* and *year*."""
        requests = scheduling.request_esaf(
            esaf_id, self.station_name, self._bss_context
        )
        return await self.serve_requests(requests)

    async def proposals(
        self, beamline: str = "", cycle: str | None = None
    ) -> list[scheduling.Proposal]:
        """Load the proposals for a given *beamline* during a given *cycle*."""
        requests = scheduling.request_proposals(
            beamline=beamline,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return await self.serve_requests(requests)

    async def proposal(
        self, proposal_id: str, cycle: str | None = None
    ) -> scheduling.Proposal:
        """Load the given proposal on a given *beamline* during a given *cycle*."""
        requests = scheduling.request_proposal(
            proposal_id=proposal_id,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return await self.serve_requests(requests)

    async def experiments(self):
        requests = ds.request_experiments(
            station_name=self.station_name,
            context=self._ds_context,
        )
        return await self.serve_requests(requests)

    async def experiment(self, id: str = "", name: str = ""):
        """Retrieve a single experiment, either by id or name."""
        requests = ds.request_experiment(
            id=id,
            name=name,
            station_name=self.station_name,
            context=self._ds_context,
        )
        return await self.serve_requests(requests)

    async def workflows(self):
        requests = processing.request_workflows(
            owner=self.username,
            context=self._proc_context,
        )
        return await self.serve_requests(requests)

    async def processing_jobs(
        self, limit: int = 5000, offset: int = 0
    ) -> list[processing.Job]:
        """Retrieve a list of jobs from the processing API.

        Parameters
        ==========
        limit
          The maximum number of jobs entries to fetch.
        offset
          Where in the list of jobs to start.

        """
        requests = processing.request_jobs(
            limit=limit,
            offset=offset,
            owner=self.username,
            context=self._proc_context,
        )
        return await self.serve_requests(requests)

    async def submit_processing_job(
        self, workflow: str, **kwargs
    ) -> list[processing.Job]:
        """Submit a new job to the processing API.

        Parameters
        ==========
        workflow
          The name of the workflow to execute.
        **kwargs
          Variables to pass to the job.
        """
        requests = processing.submit_job(
            workflow=workflow,
            job_args=kwargs,
            owner=self.username,
            context=self._proc_context,
        )
        return await self.serve_requests(requests)


class SyncClient(Client):
    """Client for the APS data management REST API.

    REST API Endpoints
    ==================

    - /dm/esaf/stationEsafs/{station_name*}/{beamline_name*}?year={year}
    - /dm/esaf/stationEsafsById/{station_name*}/{esaf_id}
    - /dm/scheduling/stationProposals/{station_name*}/{beamline_name*}?runName={run}
    - /dm/scheduling/stationProposalsById/{station_name*}/{proposal_id}?runName={run}

    * double base64 encoded bytestring
    """

    Context = SyncContext

    def serve_requests(self, requests):
        # Do the requests one at a time
        response = None
        return_value = None
        while True:
            try:
                request = requests.send(response)
            except StopIteration as exc:
                return_value = exc.value
                break
            response = request.http_client.send(request.http_request)
            response = raise_for_status(response).text
        return return_value

    def esafs(
        self, beamline: str = "", year: str | None = None
    ) -> list[scheduling.Esaf]:
        """Load the ESAF's for the given *beamline* and *year*."""
        requests = scheduling.request_esafs(
            beamline=beamline,
            year=year,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return self.serve_requests(requests)

    def esaf(self, esaf_id: str) -> scheduling.Esaf:
        """Load the ESAF's for the given *sector* and *year*."""
        requests = scheduling.request_esaf(
            esaf_id, self.station_name, self._bss_context
        )
        return self.serve_requests(requests)

    def proposals(
        self, beamline: str = "", cycle: str | None = None
    ) -> list[scheduling.Proposal]:
        """Load the proposals for a given *beamline* during a given *cycle*."""
        requests = scheduling.request_proposals(
            beamline=beamline,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return self.serve_requests(requests)

    def proposal(
        self, proposal_id: str, cycle: str | None = None
    ) -> scheduling.Proposal:
        """Load the given proposal on a given *beamline* during a given *cycle*."""
        requests = scheduling.request_proposal(
            proposal_id=proposal_id,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return self.serve_requests(requests)

    def experiments(self):
        requests = ds.request_experiments(
            station_name=self.station_name,
            context=self._ds_context,
        )
        return self.serve_requests(requests)

    def experiment(self, id: str = "", name: str = ""):
        """Retrieve a single experiment, either by id or name."""
        requests = ds.request_experiment(
            id=id,
            name=name,
            station_name=self.station_name,
            context=self._ds_context,
        )
        return self.serve_requests(requests)

    def workflows(self):
        requests = processing.request_workflows(
            owner=self.username,
            context=self._proc_context,
        )
        return self.serve_requests(requests)

    def processing_jobs(
        self, limit: int = 5000, offset: int = 0
    ) -> list[processing.Job]:
        """Retrieve a list of jobs from the processing API.

        Parameters
        ==========
        limit
          The maximum number of jobs entries to fetch.
        offset
          Where in the list of jobs to start.

        """
        requests = processing.request_jobs(
            owner=self.username,
            limit=limit,
            offset=offset,
            context=self._proc_context,
        )
        return self.serve_requests(requests)

    def submit_processing_job(self, workflow: str, **kwargs) -> list[processing.Job]:
        """Submit a new job to the processing API.

        Parameters
        ==========
        workflow
          The name of the workflow to execute.
        **kwargs
          Variables to pass to the job.
        """
        requests = processing.submit_job(
            owner=self.username,
            workflow=workflow,
            job_args=kwargs,
            context=self._proc_context,
        )
        return self.serve_requests(requests)


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
