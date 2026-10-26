from models.client import Client


class ClientDAO:
    def __init__(self, session):
        self.session = session

    def list(self):
        return self.session.query(Client).order_by(Client.id).all()

    def get(self, client_id):
        return self.session.get(Client, client_id)

    def get_by_membership(self, membership):
        return self.session.query(Client).filter_by(membership=membership).first()

    def add(self, client):
        self.session.add(client)

    def update(self, client, fields):
        for name, value in fields.items():
            setattr(client, name, value)

    def delete(self, client):
        self.session.delete(client)
