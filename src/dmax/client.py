import httpx

from . import data_storage as ds
from . import processing, scheduling
from .auth import DMAuth
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


class AsyncClient:
    """Client for the APS data management REST API."""

    def __init__(
        self,
        username: str,
        password: str,
        station_name: str,
        scheduling_uri: str = "http://localhost:11337/dm",
        data_storage_uri: str = "http://localhost:22237/dm",
        processing_uri: str = "http://localhost:55536/dm",
    ):
        """*username*, *password*, and *station_name* are all assigned by the
        data management group.

        """
        self.username = username
        self.password = password
        self.station_name = station_name
        auth = DMAuth(username=username, password=password, base_uri=scheduling_uri)
        self._bss_context = AsyncContext(base_uri=scheduling_uri, auth=auth)
        auth = DMAuth(username=username, password=password, base_uri=data_storage_uri)
        self._ds_context = AsyncContext(base_uri=data_storage_uri, auth=auth)
        auth = DMAuth(username=username, password=password, base_uri=processing_uri)
        self._proc_context = AsyncContext(base_uri=processing_uri, auth=auth)

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
            owner=self.username,
            limit=limit,
            offset=offset,
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
            owner=self.username,
            workflow=workflow,
            job_args=kwargs,
            context=self._proc_context,
        )
        return await self.serve_requests(requests)


class SyncClient:
    """Client for the APS data management REST API.

    REST API Endpoints
    ==================

    - /dm/esaf/stationEsafs/{station_name*}/{beamline_name*}?year={year}
    - /dm/esaf/stationEsafsById/{station_name*}/{esaf_id}
    - /dm/scheduling/stationProposals/{station_name*}/{beamline_name*}?runName={run}
    - /dm/scheduling/stationProposalsById/{station_name*}/{proposal_id}?runName={run}

    * double base64 encoded bytestring
    """

    base_uri: str
    auth: httpx.Auth
    ContextClass: SyncContext

    def __init__(
        self,
        username: str,
        password: str,
        station_name: str,
        scheduling_uri: str = "http://localhost:11337/dm",
        data_storage_uri: str = "http://localhost:22237/dm",
        processing_uri: str = "http://localhost:55536/dm",
    ):
        """*username*, *password*, and *station_name* are all assigned by the
        data management group.

        """
        self.username = username
        self.password = password
        self.station_name = station_name
        auth = DMAuth(username=username, password=password, base_uri=scheduling_uri)
        self._bss_context = SyncContext(base_uri=scheduling_uri, auth=auth)
        auth = DMAuth(username=username, password=password, base_uri=data_storage_uri)
        self._ds_context = SyncContext(base_uri=data_storage_uri, auth=auth)
        auth = DMAuth(username=username, password=password, base_uri=processing_uri)
        self._proc_context = SyncContext(base_uri=processing_uri, auth=auth)

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
