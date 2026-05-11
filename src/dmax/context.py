from base64 import b64encode
from collections.abc import Generator
from dataclasses import dataclass
from typing import TypeAlias, TypeVar

import httpx


def encode(string: str) -> bytes:
    """Double-base64 encoded version of the input *string*."""
    return b64encode(b64encode(string.encode()))


@dataclass
class Request:
    http_client: httpx.AsyncClient | httpx.Client
    http_request: httpx.Request


T = TypeVar("T")

RequestGenerator: TypeAlias = Generator[Request, httpx.Response, T]


def standardize_uri(uri):
    """Remove trailing characters, etc so we all agree on URI structure."""
    uri = uri.rstrip("/")
    if uri.split("/")[-1] != "dm":
        # Add the 'dm' prefix for paths
        uri = f"{uri}/dm"
    return uri


class SyncContext:
    _client: httpx.Client
    ClientClass = httpx.Client

    def __init__(self, auth, base_uri: str):
        # Standardize the host URI
        self.auth = auth
        self.base_uri = standardize_uri(base_uri)

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
