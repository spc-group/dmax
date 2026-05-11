"""Tests for features in the client that aren't for a specific data management API."""

from dmax import Client


def test_env_uris(monkeypatch):
    """Do client parameters get loaded from environmental variables?

    Example environment
    ===================

    ```sh
    DM_EXPERIMENT_ISOLATION_SETTINGS_FILE=
    DM_BEAMLINE_MANAGERS=d85674,d11049
    DM_DS_WEB_SERVICE_URL=https://example.com:22237
    DM_INSTALL_DIR=/home/dm_idc
    DM_BEAMLINE_NAME=255-ID-Z
    DM_VAR_DIR=/home/dm_idc/var
    DM_NODE_DIR=/home/dm_idc/opt/node_modules
    DM_BEAMLINE_USER_ACCOUNT=dummy_user
    DM_GLOBUS_GROUP_ADMINS=
    DM_ROOT_DIR=/home/dm_idc/production
    DM_STATION_NAME=25IDC
    DM_ETC_DIR=/home/dm_idc/etc
    DM_CONDA_DIR=/home/dm_idc/opt/conda
    DM_CAT_WEB_SERVICE_URL=https://example.com:44436
    DM_STATION_GUI_USE_ESAF_DB=
    DM_ALLOWED_EXPERIMENT_TYPES=255IDZ,TEST
    DM_PROC_WEB_SERVICE_URL=https://example.com:55536
    DM_DATA_DIRECTORY_MAP=
    DM_APS_DB_WEB_SERVICE_URL=https://example.com:11337
    LOADEDMODULES=
    DM_HOST_ARCH=linux-x86_64
    DM_LOGIN_FILE=/home/dm_idc/etc/.s25idcuser.system.login
    DM_GLOBUS_GROUP_MANAGERS=
    DM_MANAGED_DIRECTORY_STRUCTURE=1
    DM_DAQ_WEB_SERVICE_URL=https://example.com:33336
    DM_ESAF_SECTOR=25
    DM_BEAMLINE_ADMIN_ACCOUNT=dummy_staff
    DM_OPT_DIR=/home/dm_idc/opt
    ```
    """
    params = {
        "DM_APS_DB_WEB_SERVICE_URL": "https://example.com:11337",
        "DM_DS_WEB_SERVICE_URL": "https://example.com:22237",
        "DM_PROC_WEB_SERVICE_URL": "https://example.com:55536",
        "DM_STATION_NAME": "255IDZ",
    }
    for key, value in params.items():
        monkeypatch.setenv(key, value, prepend=False)
    client = Client(username="dummy_user", password="secret")
    assert client.station_name == "255IDZ"
    assert client._bss_context.base_uri == "https://example.com:11337/dm"
    assert client._ds_context.base_uri == "https://example.com:22237/dm"
    assert client._proc_context.base_uri == "https://example.com:55536/dm"


def test_station_uris():
    """Does the client guess URIs by default based on station name."""
    client = Client(station_name="25IDC")
    assert client._ds_context.base_uri == "https://s25idcdm.xray.aps.anl.gov:22237/dm"
    # BSS URI should not be guessed
    assert client._bss_context.base_uri == "https://xraydtn03.xray.aps.anl.gov:11337/dm"


def test_env_login(monkeypatch, tmp_path):
    """Do client parameters get loaded from environmental variables?

    Example environment
    ===================

    ```sh
    DM_EXPERIMENT_ISOLATION_SETTINGS_FILE=
    DM_BEAMLINE_MANAGERS=d85674,d11049
    DM_DS_WEB_SERVICE_URL=https://example.com:22237
    DM_INSTALL_DIR=/home/dm_idc
    DM_BEAMLINE_NAME=255-ID-Z
    DM_VAR_DIR=/home/dm_idc/var
    DM_NODE_DIR=/home/dm_idc/opt/node_modules
    DM_BEAMLINE_USER_ACCOUNT=dummy_user
    DM_GLOBUS_GROUP_ADMINS=
    DM_ROOT_DIR=/home/dm_idc/production
    DM_STATION_NAME=25IDC
    DM_ETC_DIR=/home/dm_idc/etc
    DM_CONDA_DIR=/home/dm_idc/opt/conda
    DM_CAT_WEB_SERVICE_URL=https://example.com:44436
    DM_STATION_GUI_USE_ESAF_DB=
    DM_ALLOWED_EXPERIMENT_TYPES=255IDZ,TEST
    DM_PROC_WEB_SERVICE_URL=https://example.com:55536
    DM_DATA_DIRECTORY_MAP=
    DM_APS_DB_WEB_SERVICE_URL=https://example.com:11337
    LOADEDMODULES=
    DM_HOST_ARCH=linux-x86_64
    DM_LOGIN_FILE=/home/dm_idc/etc/.s25idcuser.system.login
    DM_GLOBUS_GROUP_MANAGERS=
    DM_MANAGED_DIRECTORY_STRUCTURE=1
    DM_DAQ_WEB_SERVICE_URL=https://example.com:33336
    DM_ESAF_SECTOR=25
    DM_BEAMLINE_ADMIN_ACCOUNT=dummy_staff
    DM_OPT_DIR=/home/dm_idc/opt
    ```
    """
    login_path = tmp_path / "login"
    with open(login_path, mode="w") as fd:
        fd.write("dummy_user:secret")
    monkeypatch.setenv("DM_LOGIN_FILE", str(login_path), prepend=False)
    client = Client()
    assert client.username == "dummy_user"
    assert client.password == "secret"
