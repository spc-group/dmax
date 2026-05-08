import httpx


class DMAuth(httpx.Auth):

    def __init__(self, username: str, password: str, base_uri: str):
        self.username = username
        self.password = password
        self.base_uri = base_uri

    def auth_flow(self, request: httpx.Request):
        # Try the original request first, maybe we don't need to log in
        response = yield request
        if response.status_code == 401:
            # Make an extra login request to get the session cookie
            login_url = f"{self.base_uri}/login"
            response = yield httpx.Request(
                method="POST",
                url=login_url,
                data={"username": self.username, "password": self.password},
            )
            # Authentication was successful, try the original request again
            if response.status_code == 200:
                request.headers["cookie"] = response.headers["set-cookie"]
                yield request
            else:
                return response
