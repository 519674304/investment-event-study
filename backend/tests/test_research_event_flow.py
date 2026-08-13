from pathlib import Path

from fastapi.testclient import TestClient

from event_study.api.app import create_app


def client_for(tmp_path: Path) -> TestClient:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    return TestClient(create_app(database_url=database_url))


def create_object(client: TestClient, code: str, name: str) -> dict:
    response = client.post(
        "/api/research-objects",
        json={
            "market": "CN",
            "code": code,
            "name": name,
            "type": "concept_index" if code.startswith("88") else "stock",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_shared_event_survives_research_object_deletion(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    hog_index = create_object(client, "884275", "生猪养殖")
    muyuan = create_object(client, "002714", "牧原股份")

    event_response = client.post(
        "/api/events",
        json={
            "publishedOn": "2026-08-09",
            "title": "7月居民猪肉价格环比上涨",
            "summary": "7月居民猪肉价格环比上涨4.1%。",
            "sourceName": "公开信息来源",
            "sourceUrl": None,
            "categoryId": "product-price",
            "tags": ["猪肉零售价"],
            "linkedResearchObjectIds": [hog_index["id"], muyuan["id"]],
        },
    )

    assert event_response.status_code == 201
    event = event_response.json()
    assert set(event["linkedResearchObjectIds"]) == {hog_index["id"], muyuan["id"]}

    delete_response = client.delete(f"/api/research-objects/{hog_index['id']}")
    assert delete_response.status_code == 204

    surviving_event = client.get(f"/api/events/{event['id']}")
    assert surviving_event.status_code == 200
    assert surviving_event.json()["linkedResearchObjectIds"] == [muyuan["id"]]


def test_recreating_same_security_returns_existing_object(tmp_path: Path) -> None:
    client = client_for(tmp_path)

    first = create_object(client, "002714", "牧原股份")
    repeated = client.post(
        "/api/research-objects",
        json={"market": "CN", "code": "002714", "name": "牧原股份", "type": "stock"},
    )

    assert repeated.status_code == 200
    assert repeated.json()["id"] == first["id"]
