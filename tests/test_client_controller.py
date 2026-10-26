import pytest

from controllers.client_controller import (
    ClientNotFoundError,
    MembershipTakenError,
    delete_client,
    get_client,
    list_clients,
    save_client,
)

FORM_DATA = {"first_name": "Carla", "last_name": "Ruiz", "membership": 500, "id": ""}


def test_save_inserts_new_client():
    save_client(FORM_DATA)

    rows = list_clients()
    assert len(rows) == 1
    assert rows[0]["first_name"] == "Carla"
    assert rows[0]["membership"] == 500


def test_save_rejects_duplicate_membership(insert_client):
    insert_client(membership=500)

    with pytest.raises(MembershipTakenError):
        save_client(FORM_DATA)

    assert len(list_clients()) == 1


def test_database_constraint_catches_race_on_insert(insert_client):
    from unittest.mock import patch

    insert_client(membership=500)

    # Simulate two requests that both pass the pre-check before either inserts.
    with patch("dao.client_dao.ClientDAO.get_by_membership", return_value=None):
        with pytest.raises(MembershipTakenError):
            save_client(FORM_DATA)

    assert len(list_clients()) == 1


def test_save_updates_existing_client(insert_client):
    client_id = insert_client(first_name="Old", membership=1)

    save_client({**FORM_DATA, "id": str(client_id), "membership": 2})

    updated = get_client(client_id)
    assert updated["first_name"] == "Carla"
    assert updated["membership"] == 2


def test_save_unknown_id_raises_not_found():
    with pytest.raises(ClientNotFoundError):
        save_client({**FORM_DATA, "id": "999"})


def test_get_client_returns_none_when_missing():
    assert get_client(999) is None


def test_delete_removes_client(insert_client):
    client_id = insert_client(membership=3)

    delete_client(client_id)

    assert get_client(client_id) is None


def test_delete_unknown_id_raises_not_found():
    with pytest.raises(ClientNotFoundError):
        delete_client(999)


def test_list_clients_returns_plain_dicts(insert_client):
    insert_client(first_name="Dana", last_name="Vega", membership=4)

    rows = list_clients()

    assert rows == [
        {
            "id": rows[0]["id"],
            "first_name": "Dana",
            "last_name": "Vega",
            "membership": 4,
        }
    ]
