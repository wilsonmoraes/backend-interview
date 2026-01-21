def test_create_user(client):
    response = client.post(
        "/users/",
        json={"name": "Maria Silva", "email": "maria@example.com"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["name"] == "Maria Silva"
    assert data["email"] == "maria@example.com"


def test_list_users_requires_auth(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_list_and_get_user(client, user, user_headers):
    list_response = client.get("/users/", headers=user_headers)

    assert list_response.status_code == 200
    users = list_response.json()
    assert len(users) == 1
    assert users[0]["id"] == user["id"]

    get_response = client.get(f"/users/{user['id']}", headers=user_headers)

    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == user["id"]
    assert fetched["email"] == user["email"]