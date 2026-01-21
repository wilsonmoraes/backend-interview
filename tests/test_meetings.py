def test_create_list_get_update_delete_meeting(client, user_headers, meeting_id):
    list_response = client.get("/meetings/", headers=user_headers)

    assert list_response.status_code == 200
    meetings = list_response.json()
    assert len(meetings) == 1
    assert meetings[0]["id"] == meeting_id

    get_response = client.get(f"/meetings/{meeting_id}", headers=user_headers)

    assert get_response.status_code == 200
    meeting = get_response.json()
    assert meeting["id"] == meeting_id
    assert meeting["notes"] == []
    assert meeting["tasks"] == []

    update_response = client.put(
        f"/meetings/{meeting_id}",
        json={"title": "Sprint Review"},
        headers=user_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Sprint Review"

    delete_response = client.delete(f"/meetings/{meeting_id}", headers=user_headers)

    assert delete_response.status_code == 204

    missing_response = client.get(f"/meetings/{meeting_id}", headers=user_headers)
    assert missing_response.status_code == 404