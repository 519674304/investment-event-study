from pathlib import Path

from fastapi.testclient import TestClient

from event_study.api.app import create_app


def client_for(database_path: Path) -> TestClient:
    return TestClient(create_app(database_url=f"sqlite:///{database_path}"))


def create_object(client: TestClient, code: str, name: str) -> dict:
    response = client.post(
        "/api/research-objects",
        json={"market": "CN", "code": code, "name": name, "type": "stock"},
    )
    assert response.status_code == 201
    return response.json()


def create_event(client: TestClient, object_id: str) -> dict:
    response = client.post(
        "/api/events",
        json={
            "publishedOn": "2026-08-09",
            "title": "原始标题",
            "summary": "原始摘要",
            "sourceName": None,
            "sourceUrl": None,
            "categoryId": "other",
            "tags": [],
            "linkedResearchObjectIds": [object_id],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_lists_research_objects_after_restart(tmp_path: Path) -> None:
    database_path = tmp_path / "persistent.db"
    first_client = client_for(database_path)
    created = create_object(first_client, "002714", "牧原股份")

    restarted_client = client_for(database_path)
    response = restarted_client.get("/api/research-objects")

    assert response.status_code == 200
    assert response.json() == [created]


def test_updates_event_content_and_links_atomically(tmp_path: Path) -> None:
    client = client_for(tmp_path / "edit.db")
    muyuan = create_object(client, "002714", "牧原股份")
    wens = create_object(client, "300498", "温氏股份")
    event = create_event(client, muyuan["id"])

    response = client.put(
        f"/api/events/{event['id']}",
        json={
            "publishedOn": "2026-08-10",
            "title": "修改后的标题",
            "summary": "修改后的摘要",
            "sourceName": "人工补录",
            "sourceUrl": None,
            "categoryId": "industry-supply-demand",
            "tags": ["能繁母猪"],
            "linkedResearchObjectIds": [muyuan["id"], wens["id"]],
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "修改后的标题"
    assert response.json()["publishedOn"] == "2026-08-10"
    assert response.json()["tags"] == ["能繁母猪"]
    assert set(response.json()["linkedResearchObjectIds"]) == {muyuan["id"], wens["id"]}


def test_deletes_event_from_storage(tmp_path: Path) -> None:
    client = client_for(tmp_path / "delete.db")
    research_object = create_object(client, "002714", "牧原股份")
    event = create_event(client, research_object["id"])

    response = client.delete(f"/api/events/{event['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/events/{event['id']}").status_code == 404


def test_lists_events_for_one_research_object_newest_first(tmp_path: Path) -> None:
    client = client_for(tmp_path / "event-list.db")
    muyuan = create_object(client, "002714", "牧原股份")
    wens = create_object(client, "300498", "温氏股份")
    older = create_event(client, muyuan["id"])
    newer_payload = {
        **older,
        "publishedOn": "2026-08-11",
        "title": "较新事件",
        "linkedResearchObjectIds": [muyuan["id"], wens["id"]],
    }
    newer_payload.pop("id")
    newer = client.post("/api/events", json=newer_payload).json()

    response = client.get(f"/api/events?researchObjectId={muyuan['id']}")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [newer["id"], older["id"]]
    assert client.get(f"/api/events?researchObjectId={wens['id']}").json() == [newer]


def test_event_can_be_created_unlinked(tmp_path: Path) -> None:
    client = client_for(tmp_path / "unlinked-event.db")

    response = client.post(
        "/api/events",
        json={
            "publishedOn": "2026-08-12",
            "title": "待关联事件",
            "summary": None,
            "sourceName": "人工补录",
            "sourceUrl": None,
            "categoryId": None,
            "tags": [],
            "linkedResearchObjectIds": [],
        },
    )

    assert response.status_code == 201
    assert response.json()["linkedResearchObjectIds"] == []


def test_event_survives_deletion_of_its_last_research_object(tmp_path: Path) -> None:
    client = client_for(tmp_path / "orphan-event.db")
    research_object = create_object(client, "002714", "牧原股份")
    linked_event = create_event(client, research_object["id"])

    delete_response = client.delete(f"/api/research-objects/{research_object['id']}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/events/{linked_event['id']}").json()["linkedResearchObjectIds"] == []
