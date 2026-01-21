def test_create_list_get_note(client, user_headers, meeting_id):
    create_response = client.post(
        "/notes/",
        json={"content": "Discussion notes", "meeting_id": meeting_id},
        headers=user_headers,
    )

    assert create_response.status_code == 201
    note = create_response.json()
    assert note["meeting_id"] == meeting_id

    list_response = client.get(f"/notes/?meeting_id={meeting_id}", headers=user_headers)

    assert list_response.status_code == 200
    notes = list_response.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note["id"]

    get_response = client.get(f"/notes/{note['id']}", headers=user_headers)

    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == note["id"]
    assert fetched["content"] == "Discussion notes"