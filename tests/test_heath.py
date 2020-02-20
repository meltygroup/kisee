async def test_health(client):
    response = await client.get("/health")
    assert response.status == 200
    body = await response.json()
    assert body["status"] == "green"


async def test_health_bad_db(client, monkeypatch):
    async def is_connection_alive():
        return False

    monkeypatch.setattr(
        client.app["identity_backend"], "is_connection_alive", is_connection_alive
    )
    response = await client.get("/health")
    assert response.status == 200
    body = await response.json()
    assert body["status"] == "red"
