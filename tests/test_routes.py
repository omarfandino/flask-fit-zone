import re

from controllers.client_controller import list_clients


def test_index_lists_clients_with_english_labels(web, insert_client):
    insert_client(first_name="Daniel", last_name="Torres", membership=100)

    body = web.get("/").get_data(as_text=True)

    assert web.get("/").status_code == 200
    assert "Daniel" in body
    assert "First name" in body
    assert "Membership" in body
    assert 'value="Save"' in body


def test_edit_prefills_form_with_client_data(web, insert_client):
    client_id = insert_client(first_name="Ivonne", last_name="Lopez", membership=200)

    response = web.get(f"/edit/{client_id}")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'value="Ivonne"' in body
    assert f'value="{client_id}"' in body
    # A relative action would post to /edit/save from this page.
    assert 'action="/save"' in body


def test_edit_unknown_client_returns_404(web):
    assert web.get("/edit/999").status_code == 404


def test_save_creates_client_and_redirects(web):
    response = web.post(
        "/save",
        data={"first_name": "Sofia", "last_name": "Hernandez", "membership": "300"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert [row["first_name"] for row in list_clients()] == ["Sofia"]


def test_save_shows_error_when_membership_is_taken(web, insert_client):
    insert_client(membership=300)

    response = web.post(
        "/save",
        data={"first_name": "Sofia", "last_name": "Hernandez", "membership": "300"},
    )

    assert response.status_code == 200
    assert "That membership already exists." in response.get_data(as_text=True)
    assert len(list_clients()) == 1


def test_save_unknown_client_id_returns_404(web):
    response = web.post(
        "/save",
        data={
            "id": "999",
            "first_name": "Sofia",
            "last_name": "Hernandez",
            "membership": "300",
        },
    )

    assert response.status_code == 404


def test_clean_redirects_to_index(web):
    response = web.get("/clean")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_save_invalid_form_shows_validation_errors(web):
    response = web.post(
        "/save", data={"first_name": "", "last_name": "", "membership": ""}
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "This field is required." in body
    assert list_clients() == []


def test_delete_removes_client_and_redirects(web, insert_client):
    client_id = insert_client(membership=400)

    response = web.post(f"/delete/{client_id}")

    assert response.status_code == 302
    assert list_clients() == []


def test_delete_unknown_client_returns_404(web):
    assert web.post("/delete/999").status_code == 404


def test_delete_does_not_accept_get(web, insert_client):
    client_id = insert_client(membership=401)

    assert web.get(f"/delete/{client_id}").status_code == 405
    assert len(list_clients()) == 1


def test_post_without_csrf_token_is_rejected(app, insert_client):
    client_id = insert_client(membership=402)
    app.config["WTF_CSRF_ENABLED"] = True
    web = app.test_client()

    response = web.post(f"/delete/{client_id}")

    assert response.status_code == 400
    assert len(list_clients()) == 1


def test_post_with_page_csrf_token_is_accepted(app, insert_client):
    client_id = insert_client(membership=403)
    app.config["WTF_CSRF_ENABLED"] = True
    web = app.test_client()
    page = web.get("/").get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)

    response = web.post(f"/delete/{client_id}", data={"csrf_token": token})

    assert response.status_code == 302
    assert list_clients() == []
