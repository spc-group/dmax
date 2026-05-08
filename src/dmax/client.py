import httpx

from . import bss
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
    if "errorCode" not in content and "errorMessage" not in content:
        # Everything is fine, just send the response on
        return response
    error_code = content.get("errorCode", "??")
    error_message = content.get("errorMessage", "Unknown error")
    raise httpx.HTTPStatusError(
        f"{error_message} ({error_code})", response=response, request=response.request
    )


class AsyncClient:
    """Client for the APS data management REST API."""

    def __init__(self, username: str, password: str, station_name: str, bss_uri: str):
        """*username*, *password*, and *station_name* are all assigned by the
        data management group.

        """
        self.station_name = station_name
        auth = DMAuth(username=username, password=password, base_uri=bss_uri)
        self._bss_context = AsyncContext(base_uri=bss_uri, auth=auth)

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
    ) -> list[bss.Esaf]:
        """Load the ESAF's for the given *beamline* and *year*."""
        requests = bss.request_esafs(
            beamline=beamline,
            year=year,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return await self.serve_requests(requests)

    async def esaf(self, esaf_id: str) -> bss.Esaf:
        """Load the ESAF's for the given *sector* and *year*."""
        requests = bss.request_esaf(esaf_id, self.station_name, self._bss_context)
        return await self.serve_requests(requests)

    async def proposals(
        self, beamline: str = "", cycle: str | None = None
    ) -> list[bss.Proposal]:
        """Load the proposals for a given *beamline* during a given *cycle*."""
        requests = bss.request_proposals(
            beamline=beamline,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return await self.serve_requests(requests)

    async def proposal(
        self, proposal_id: str, cycle: str | None = None
    ) -> bss.Proposal:
        """Load the given proposal on a given *beamline* during a given *cycle*."""
        requests = bss.request_proposal(
            proposal_id=proposal_id,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return await self.serve_requests(requests)


class SyncClient:
    """Client for the APS data management REST API.

    REST API Endpoints
    ==================

    - /dm/esaf/stationEsafs/{station_name*}/{beamline_name*}?year={year}
    - /dm/esaf/stationEsafsById/{station_name*}/{esaf_id}
    - /dm/bss/stationProposals/{station_name*}/{beamline_name*}?runName={run}
    - /dm/bss/stationProposalsById/{station_name*}/{proposal_id}?runName={run}

    * double base64 encoded bytestring
    """

    base_uri: str
    auth: httpx.Auth
    ContextClass: SyncContext

    def __init__(self, username: str, password: str, station_name: str, bss_uri: str):
        """*username*, *password*, and *station_name* are all assigned by the
        data management group.

        """
        self.station_name = station_name
        auth = DMAuth(username=username, password=password, base_uri=bss_uri)
        self._bss_context = SyncContext(base_uri=bss_uri, auth=auth)

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

    def esafs(self, beamline: str = "", year: str | None = None) -> list[bss.Esaf]:
        """Load the ESAF's for the given *beamline* and *year*."""
        requests = bss.request_esafs(
            beamline=beamline,
            year=year,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return self.serve_requests(requests)

    def esaf(self, esaf_id: str) -> bss.Esaf:
        """Load the ESAF's for the given *sector* and *year*."""
        requests = bss.request_esaf(esaf_id, self.station_name, self._bss_context)
        return self.serve_requests(requests)

    def proposals(
        self, beamline: str = "", cycle: str | None = None
    ) -> list[bss.Proposal]:
        """Load the proposals for a given *beamline* during a given *cycle*."""
        requests = bss.request_proposals(
            beamline=beamline,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return self.serve_requests(requests)

    def proposal(self, proposal_id: str, cycle: str | None = None) -> bss.Proposal:
        """Load the given proposal on a given *beamline* during a given *cycle*."""
        requests = bss.request_proposal(
            proposal_id=proposal_id,
            cycle=cycle,
            station_name=self.station_name,
            context=self._bss_context,
        )
        return self.serve_requests(requests)
