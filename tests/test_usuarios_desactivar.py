import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_desactivar_usuario_payload():
    # Suponiendo que el usuario 1 existe y no es el usuario autenticado
    # Aquí deberías autenticarte si tu API lo requiere (agregar headers)
    response = client.patch(
        "/api/usuarios/desactivar",
        json={"usuario_id": 1}
    )
    assert response.status_code in (200, 401, 403, 404)  # 200 si OK, 401/403 si no autenticado, 404 si no existe
    if response.status_code == 200:
        data = response.json()
        assert data["id"] == 1
        assert data["estado"] == "INACTIVO"

def test_desactivar_usuario_payload_falta_id():
    response = client.patch("/api/usuarios/desactivar", json={})
    assert response.status_code == 400
    assert "usuario_id" in response.text or "entero" in response.text

def test_desactivar_usuario_payload_id_invalido():
    response = client.patch("/api/usuarios/desactivar", json={"usuario_id": "no-num"})
    assert response.status_code == 400
    assert "usuario_id" in response.text or "entero" in response.text
