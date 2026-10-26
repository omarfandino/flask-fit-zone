from sqlalchemy.exc import IntegrityError

from dao.client_dao import ClientDAO
from models.client import Client
from models.database import get_session


class MembershipTakenError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


def list_clients():
    with get_session() as session:
        dao = ClientDAO(session)
        return [
            {
                "id": client.id,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "membership": client.membership,
            }
            for client in dao.list()
        ]


def get_client(client_id):
    with get_session() as session:
        dao = ClientDAO(session)
        client = dao.get(client_id)
        if client is None:
            return None
        return {
            "id": client.id,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "membership": client.membership,
        }


def delete_client(client_id):
    with get_session() as session:
        dao = ClientDAO(session)
        client = dao.get(client_id)
        if client is None:
            raise ClientNotFoundError(client_id)
        dao.delete(client)


def save_client(data):
    fields = {
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "membership": data["membership"],
    }
    try:
        with get_session() as session:
            dao = ClientDAO(session)
            client_id = int(data["id"]) if data["id"] else None
            client = dao.get(client_id) if client_id is not None else None
            if client_id is not None and client is None:
                raise ClientNotFoundError(client_id)

            taken = dao.get_by_membership(fields["membership"])
            if taken and (client is None or taken.id != client.id):
                raise MembershipTakenError(fields["membership"])

            if client is None:
                dao.add(Client(**fields))
            else:
                dao.update(client, fields)
    except IntegrityError as error:
        raise MembershipTakenError(fields["membership"]) from error
