from unittest.mock import MagicMock, patch

import pytest

from controllers.client_controller import (
    ClientNotFoundError,
    MembershipTakenError,
    save_client,
)
from models.client import Client

FORM_DATA = {"first_name": "Ana", "last_name": "Lopez", "membership": 300, "id": ""}


@pytest.fixture
def dao():
    """Replaces ClientDAO with a mock, so no database is involved."""
    with patch("controllers.client_controller.get_session"), patch(
        "controllers.client_controller.ClientDAO"
    ) as dao_class:
        dao_mock = MagicMock()
        dao_class.return_value = dao_mock
        dao_mock.get_by_membership.return_value = None
        yield dao_mock


def test_new_client_is_added_when_membership_is_free(dao):
    save_client(FORM_DATA)

    dao.add.assert_called_once()
    added = dao.add.call_args.args[0]
    assert isinstance(added, Client)
    assert (added.first_name, added.last_name, added.membership) == (
        "Ana",
        "Lopez",
        300,
    )
    dao.update.assert_not_called()


def test_new_client_is_rejected_when_membership_is_taken(dao):
    dao.get_by_membership.return_value = Client(id=9, membership=300)

    with pytest.raises(MembershipTakenError):
        save_client(FORM_DATA)

    dao.add.assert_not_called()


def test_existing_client_is_updated(dao):
    existing = Client(id=4, first_name="Old", last_name="Name", membership=100)
    dao.get.return_value = existing

    save_client({**FORM_DATA, "id": "4"})

    dao.get.assert_called_once_with(4)
    dao.update.assert_called_once_with(
        existing, {"first_name": "Ana", "last_name": "Lopez", "membership": 300}
    )
    dao.add.assert_not_called()


def test_editing_keeps_own_membership_without_error(dao):
    existing = Client(id=4, first_name="Old", last_name="Name", membership=300)
    dao.get.return_value = existing
    dao.get_by_membership.return_value = existing

    save_client({**FORM_DATA, "id": "4"})

    dao.update.assert_called_once()


def test_editing_to_another_clients_membership_is_rejected(dao):
    dao.get.return_value = Client(id=4, membership=100)
    dao.get_by_membership.return_value = Client(id=9, membership=300)

    with pytest.raises(MembershipTakenError):
        save_client({**FORM_DATA, "id": "4"})

    dao.update.assert_not_called()


def test_unknown_id_raises_not_found(dao):
    dao.get.return_value = None

    with pytest.raises(ClientNotFoundError):
        save_client({**FORM_DATA, "id": "999"})

    dao.add.assert_not_called()
    dao.update.assert_not_called()
