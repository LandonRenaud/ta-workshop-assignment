import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    """Provide an isolated Flask test client for each test."""
    monkeypatch.setattr(
        app_module,
        "tasks",
        [
            {"id": 1, "title": "Project-1 Report"},
            {"id": 2, "title": "Project-2 MMFs"},
        ],
    )
    monkeypatch.setattr(app_module, "next_id", 3)
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as test_client:
        yield test_client


def test_index(client):
    """Render the task tracker index page successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"Task Tracker" in response.data
    assert b"task-priority" in response.data


def test_get_tasks(client):
    """Return all tasks with Medium for legacy tasks without priority."""
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "title": "Project-1 Report",
            "priority": "Medium",
        },
        {
            "id": 2,
            "title": "Project-2 MMFs",
            "priority": "Medium",
        },
    ]


@pytest.mark.parametrize("priority", ["Low", "Medium", "High"])
def test_add_task_with_each_priority(client, priority):
    """Create and retrieve a task for every supported priority."""
    response = client.post(
        "/api/tasks",
        json={"title": f"{priority} task", "priority": priority},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": f"{priority} task",
        "priority": priority,
    }

    tasks_response = client.get("/api/tasks")
    assert tasks_response.status_code == 200
    assert tasks_response.get_json()[-1]["priority"] == priority


def test_add_task_success(client):
    """Create a task with an explicitly supplied priority."""
    response = client.post(
        "/api/tasks",
        json={"title": "New task", "priority": "High"},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "New task",
        "priority": "High",
    }


def test_add_task_defaults_to_medium_priority(client):
    """Assign Medium when a task request omits priority."""
    response = client.post("/api/tasks", json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "Default task",
        "priority": "Medium",
    }

    tasks_response = client.get("/api/tasks")
    assert tasks_response.get_json()[-1]["priority"] == "Medium"


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities outside the supported set."""
    response = client.post(
        "/api/tasks",
        json={"title": "Invalid task", "priority": "Urgent"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Priority must be Low, Medium, or High"
    }

    tasks_response = client.get("/api/tasks")
    assert len(tasks_response.get_json()) == 2


def test_get_tasks_serializes_existing_task_without_priority(client):
    """Expose Medium for persisted tasks without a priority field."""
    app_module.tasks.append({"id": 3, "title": "Legacy task"})

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json()[-1] == {
        "id": 3,
        "title": "Legacy task",
        "priority": "Medium",
    }


def test_add_task_missing_title(client):
    """Reject task creation requests without a title."""
    response = client.post("/api/tasks", json={"priority": "Low"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_delete_task(client):
    """Delete a task by ID and return a success response."""
    response = client.delete("/api/tasks/1")

    assert response.status_code == 200
    assert response.get_json() == {"result": "success"}
    assert [task["id"] for task in client.get("/api/tasks").get_json()] == [2]
