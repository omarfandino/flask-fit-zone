import pytest
from sqlalchemy.exc import IntegrityError

from dao.client_dao import ClientDAO
from models.database import get_session


def test_add_persists_client_and_assigns_id(insert_client):
    client_id = insert_client(first_name="Bruno", membership=10)

    with get_session() as session:
        found = ClientDAO(session).get(client_id)
        assert found.first_name == "Bruno"
        assert found.membership == 10


def test_list_returns_clients_ordered_by_id(insert_client):
    first = insert_client(membership=1)
    second = insert_client(membership=2)

    with get_session() as session:
        ids = [client.id for client in ClientDAO(session).list()]

    assert ids == [first, second]


def test_get_returns_none_for_unknown_id():
    with get_session() as session:
        assert ClientDAO(session).get(12345) is None


def test_get_by_membership_finds_matching_client(insert_client):
    client_id = insert_client(membership=77)

    with get_session() as session:
        found = ClientDAO(session).get_by_membership(77)
        assert found.id == client_id

        assert ClientDAO(session).get_by_membership(78) is None


def test_update_changes_fields_of_loaded_client(insert_client):
    client_id = insert_client(first_name="Old", membership=5)

    with get_session() as session:
        dao = ClientDAO(session)
        client = dao.get(client_id)
        dao.update(client, {"first_name": "New", "last_name": "Name", "membership": 6})

    with get_session() as session:
        updated = ClientDAO(session).get(client_id)
        assert (updated.first_name, updated.last_name, updated.membership) == (
            "New",
            "Name",
            6,
        )


def test_delete_removes_client(insert_client):
    client_id = insert_client(membership=8)

    with get_session() as session:
        dao = ClientDAO(session)
        dao.delete(dao.get(client_id))

    with get_session() as session:
        assert ClientDAO(session).get(client_id) is None


def test_database_rejects_duplicate_membership(insert_client):
    insert_client(membership=99)

    with pytest.raises(IntegrityError):
        insert_client(first_name="Other", membership=99)
