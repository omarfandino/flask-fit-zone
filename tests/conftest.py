import os

# Must be set before the models are imported, so the tests use the test database.
os.environ["DB_NAME"] = "fit_zone_test_db"
os.environ.setdefault("WTF_SECRET_KEY", "test-secret-key")

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import models.client  # noqa: F401  registers the client table in Base.metadata
from models.database import Base, engine, get_session

if "test" not in engine.url.database:
    raise RuntimeError("Tests must run against a database whose name contains 'test'")


@pytest.fixture(scope="session", autouse=True)
def database_schema():
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as error:
        reason = str(error.orig).strip() if error.orig else str(error)
        pytest.exit(
            f"Cannot prepare the test database '{engine.url.database}': {reason}\n"
            "See 'Database setup' in README.md.",
            returncode=1,
        )
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def empty_client_table():
    with get_session() as session:
        session.execute(text("TRUNCATE client RESTART IDENTITY"))
    yield


@pytest.fixture
def app():
    from app import app as flask_app

    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    yield flask_app
    flask_app.config.update(WTF_CSRF_ENABLED=False)


@pytest.fixture
def web(app):
    return app.test_client()


@pytest.fixture
def insert_client():
    from models.client import Client
    from dao.client_dao import ClientDAO

    def _insert(first_name="Ana", last_name="Lopez", membership=100):
        with get_session() as session:
            client = Client(
                first_name=first_name, last_name=last_name, membership=membership
            )
            ClientDAO(session).add(client)
            session.flush()
            return client.id

    return _insert
