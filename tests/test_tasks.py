def test_create_list_update_delete_task(client, user_headers, meeting_id):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Implement feature",
            "description": "Complete implementation",
            "due_meeting_id": meeting_id,
        },
        headers=user_headers,
    )

    assert create_response.status_code == 201
    task = create_response.json()
    assert task["due_meeting_id"] == meeting_id
    assert task["status"] == "pending"

    list_response = client.get(f"/tasks/?meeting_id={meeting_id}", headers=user_headers)

    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task["id"]

    update_response = client.put(
        f"/tasks/{task['id']}",
        json={"status": "completed"},
        headers=user_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"

    delete_response = client.delete(f"/tasks/{task['id']}", headers=user_headers)

    assert delete_response.status_code == 204

    missing_response = client.get(f"/tasks/{task['id']}", headers=user_headers)
    assert missing_response.status_code == 404