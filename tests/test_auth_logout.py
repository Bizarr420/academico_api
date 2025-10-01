import sys
import types
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub optional mysql connector dependency expected by the application modules.
mysql_module = types.ModuleType("mysql")
connector_module = types.ModuleType("mysql.connector")
connector_module.apilevel = "2.0"
connector_module.threadsafety = 1
connector_module.paramstyle = "pyformat"
connector_module.Error = RuntimeError
connector_module.OperationalError = RuntimeError
connector_module.InterfaceError = RuntimeError


def _mysql_connect(*args, **kwargs):  # pragma: no cover - defensive stub
    raise RuntimeError("mysql connector is not available in the test environment")


connector_module.connect = _mysql_connect
mysql_module.connector = connector_module
sys.modules.setdefault("mysql", mysql_module)
sys.modules.setdefault("mysql.connector", connector_module)

from app.main import app


def test_logout_clears_access_token_cookie():
    original_startup = list(app.router.on_startup)
    original_shutdown = list(app.router.on_shutdown)
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()

    try:
        with TestClient(app) as client:
            client.cookies.set("access_token", "dummy-token", path="/")

            response = client.post("/api/auth/logout")

            assert response.status_code == 204
            set_cookie_header = response.headers.get("set-cookie")
            assert set_cookie_header is not None
            assert "access_token=" in set_cookie_header
            assert "Max-Age=0" in set_cookie_header
            assert "Path=/" in set_cookie_header
            assert "SameSite=lax" in set_cookie_header
            assert "HttpOnly" in set_cookie_header
            assert response.cookies.get("access_token") in (None, "")
    finally:
        app.router.on_startup.extend(original_startup)
        app.router.on_shutdown.extend(original_shutdown)
