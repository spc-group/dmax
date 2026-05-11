from base64 import b64encode
from collections.abc import Generator
from dataclasses import dataclass
from typing import TypeAlias, TypeVar

import httpx

from .auth import DMAuth


def encode(string: str) -> bytes:
    """Double-base64 encoded version of the input *string*."""
    return b64encode(b64encode(string.encode()))


@dataclass
class Request:
    http_client: httpx.AsyncClient | httpx.Client
    http_request: httpx.Request


T = TypeVar("T")

RequestGenerator: TypeAlias = Generator[Request, httpx.Response, T]


class SyncContext:
    _client: httpx.Client
    ClientClass = httpx.Client

    def __init__(self, username: str, password: str, base_uri: str):
        # Standardize the host URI
        self.base_uri = base_uri
        self.auth = DMAuth(username=username, password=password, base_uri=self.base_uri)

    @property
    def client(self) -> httpx.AsyncClient | httpx.Client:
        if not hasattr(self, "_client"):
            # API certificates are not signed by a trusted local issuer
            # If that changes, set `verify=True`
            self._client = self.ClientClass(
                base_url=self.base_uri, auth=self.auth, verify=False
            )
        return self._client

    def get(self, url: str, *args, **kwargs):
        return self.build_request("GET", url, *args, **kwargs)

    def post(self, url: str, *args, **kwargs):
        return self.build_request("POST", url, *args, **kwargs)

    def build_request(self, method: str, url: str, *args, **kwargs):
        url = url.removesuffix("/b''")
        request = Request(
            http_client=self.client,
            http_request=self.client.build_request(method, url, *args, **kwargs),
        )
        return request


class AsyncContext(SyncContext):
    ClientClass = httpx.AsyncClient
