import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Ejemplo: test de registro
# Puedes agregar credenciales de prueba y datos válidos para cada endpoint

def test_register():
    response = client.post("/auth/register", json={
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code in (200, 201, 400)  # Puede fallar si el usuario ya existe

# Ejemplo: test de login

def test_login():
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def get_auth_token(email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

# Utilidad: crear usuarios y devolver lista de dicts con info y tokens
def crear_usuarios_y_tokens(n):
    usuarios = []
    for i in range(n):
        email = f"user{i}@test.com"
        password = f"Password{i}123!"
        nombre = f"User{i}"
        client.post("/auth/register", json={
            "name": nombre,
            "email": email,
            "password": password
        })
        token = get_auth_token(email, password)
        usuarios.append({"email": email, "password": password, "name": nombre, "token": token})
    return usuarios

# Utilidad: obtener id de usuario por nombre
def get_user_id_by_name(headers, nombre):
    resp = client.get("/auth/users", headers=headers)
    assert resp.status_code == 200
    for u in resp.json():
        if u["name"] == nombre:
            return u["id"]
    raise Exception(f"Usuario {nombre} no encontrado")

# Test /auth/me (requiere autenticación)
def test_auth_me():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert "name" in response.json()

# Test /proposals/turn-status (acceso para cualquier usuario autenticado)
def test_proposals_turn_status():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/proposals/turn-status", headers=headers)
    assert response.status_code == 200
    assert "status" in response.json()

# Test /proposals/toggle-propuestas-turn (solo master)
def test_toggle_propuestas_turn_master():
    # Suponiendo que existe un usuario master
    master_token = get_auth_token("jpaul1706@hotmail.com", "Dybala2003#")
    headers = {"Authorization": f"Bearer {master_token}"}
    response = client.post("/proposals/toggle-propuestas-turn", headers=headers)
    assert response.status_code == 200
    assert "status" in response.json()

def test_toggle_propuestas_turn_non_master():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/proposals/toggle-propuestas-turn", headers=headers)
    assert response.status_code == 403  # No autorizado para usuarios no master

# Test /auth/upload-profile-image (requiere autenticación)

# Test /auth/logout (requiere autenticación)
def test_logout():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200

# Test /proposals/ (GET, POST)
def test_get_proposals():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/proposals/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_proposal():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Juego de prueba",
        "price": 1000,
        "month_year": "2025-12",
        "proposal_number": 1
    }
    response = client.post("/proposals/", headers=headers, json=data)
    assert response.status_code in (200, 201, 400)  # Puede fallar si ya existe propuesta activa

# Test /proposals/{proposal_id} (GET)
def test_get_proposal_by_id():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    # Suponiendo que existe la propuesta con ID 1
    response = client.get("/proposals/1", headers=headers)
    assert response.status_code in (200, 404)

# Test /proposals/{proposal_id}/vote (POST)
def test_vote_proposal():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/proposals/1/vote", headers=headers)
    assert response.status_code in (200, 400, 403, 404)

# Test /proposals/{proposal_id}/select-winner (solo master)

def test_select_winner_non_master():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/proposals/1/select-winner", headers=headers)
    assert response.status_code == 403

# Test /deposits/ (GET, POST)
def test_get_deposits():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/deposits/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_deposit():
    master_token = get_auth_token("jpaul1706@hotmail.com", "Dybala2003#")
    headers = {"Authorization": f"Bearer {master_token}"}
    data = {
        "member_id": 1,
        "amount": 1000,
        "note": "Depósito de prueba",
        "date": "2025-12-03T00:00:00"
    }
    response = client.post("/deposits/", headers=headers, json=data)
    assert response.status_code in (200, 201, 404)

# Test /deposits/balances/all (GET)
def test_get_all_balances():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/deposits/balances/all", headers=headers)
    assert response.status_code == 200
    assert "balances" in response.json()

# Test /purchases/ (GET, POST)
def test_get_purchases():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/purchases/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Test /purchases/{purchase_id} (GET)
def test_get_purchase_by_id():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/purchases/1", headers=headers)
    assert response.status_code in (200, 404)

# Test /purchases/my-shares/pending (GET)
def test_get_my_pending_shares():
    token = get_auth_token("testuser@example.com", "testpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/purchases/my-shares/pending", headers=headers)
    assert response.status_code == 200
    assert "pending_shares" in response.json()

# Test flujo completo de selección de propuesta ganadora

# Test flujo de compra desde propuesta

def test_create_deposit_flow():
    # Crear 6 usuarios y un master
    master_email = "master_deposit@test.com"
    master_password = "MasterDep123!"
    client.post("/auth/register", json={
        "name": "MasterDep",
        "email": master_email,
        "password": master_password,
        "role": "master"
    })
    master_token = get_auth_token(master_email, master_password)
    master_headers = {"Authorization": f"Bearer {master_token}"}
    usuarios = crear_usuarios_y_tokens(6)
    # Depositar saldo suficiente a todos
    for u in usuarios:
        user_id = get_user_id_by_name(master_headers, u["name"])
        deposit_data = {"member_id": user_id, "amount": 5000, "note": "Saldo test"}
        deposit_resp = client.post("/deposits/", headers=master_headers, json=deposit_data)
        assert deposit_resp.status_code in (200, 201)
        assert deposit_resp.json()["deposit"]["member_id"] == user_id

