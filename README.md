# Fit Zone

A small Flask application to manage the clients of a gym: create, list, edit and delete clients, each with a name, last name and membership number.

The project is also a study project. It shows how the pieces of a typical Python web application fit together: an ORM, a data access object, a controller layer, forms with validation, CSRF protection and an automated test suite.

## Features

- List all clients.
- Create a client from a form with validation (required fields, length limits, non-negative membership).
- Edit an existing client.
- Delete a client (POST only, protected by a CSRF token).
- A membership number can belong to only one client. The check runs before saving, and the database constraint guarantees it even under concurrent requests.

## Stack

- Python 3.13
- Flask 3.1 with Jinja2 templates
- Flask-WTF and WTForms for forms, validation and CSRF protection
- SQLAlchemy 2.1 (ORM) with psycopg2
- PostgreSQL
- Bootstrap 5.3 and Bootstrap Icons, loaded from a CDN
- pytest and coverage.py for tests
- pre-commit with Black for formatting

## Architecture

The code follows an MVC-style layout:

```
app.py                  Routes (view entry points) and rendering
controllers/            Business rules and transaction boundaries
dao/                    Data access: all queries live here
models/                 SQLAlchemy models and the database session setup
forms/                  WTForms classes: fields and validation rules
templates/              Jinja2 HTML templates
tests/                  Unit, integration and route tests
schema.sql              Table definition for creating the database by hand
```

The request flow is:

```
Browser -> app.py (route) -> controllers -> dao -> models -> PostgreSQL
```

- **Controllers** open a session with `get_session()`. The session commits when the block finishes without errors, and rolls back when an error is raised.
- **DAOs** only add, read, change or delete objects. They never commit.
- **Forms** validate the input before the controller is called.

## Requirements

- Python 3.13
- PostgreSQL 10 or newer (identity columns are required)

Python packages are listed in `requirements.txt` (runtime) and `requirements-dev.txt` (runtime plus test and development tools).

## Setup

1. Clone the repository and create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. Database setup. Run these as the PostgreSQL superuser (for example `sudo -u postgres psql`). Skip the first command if you already have a role you want to use.

   ```sql
   CREATE ROLE fit_zone_user LOGIN PASSWORD 'change-me';
   CREATE DATABASE fit_zone_db OWNER fit_zone_user;
   CREATE DATABASE fit_zone_test_db OWNER fit_zone_user;
   ```

   Then create the application table, connected as that role:

   ```bash
   psql -U fit_zone_user -h localhost -d fit_zone_db -f schema.sql
   ```

   The role must **own** both databases. Since PostgreSQL 15 only the owner can create tables in the `public` schema by default, and the tests create and drop their tables on every run. The test database needs no table: the tests create it from the models.

3. Create a `.env` file from the example and fill in your values:

   ```bash
   cp .env.example .env
   ```

   | Variable        | Meaning                                              |
   |-----------------|------------------------------------------------------|
   | `DB_USER`       | PostgreSQL user                                      |
   | `DB_PASSWORD`   | Password for that user                               |
   | `DB_HOST`       | Database host, usually `localhost`                   |
   | `DB_PORT`       | Database port, usually `5432`                        |
   | `DB_NAME`       | Application database, for example `fit_zone_db`      |
   | `WTF_SECRET_KEY`| Long random string used to sign CSRF tokens          |

   Generate a secret key with:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Running the application

```bash
python app.py
```

Then open <http://127.0.0.1:5000>.

## Running the tests

The tests use `fit_zone_test_db`, with the user, password and host from `.env`. The test configuration refuses to run against any database whose name does not contain `test`, so your application data is safe. If the test database is missing or the role lacks permissions, pytest stops with a message that says what failed.

```bash
pytest -q
```

To see line and branch coverage:

```bash
coverage run -m pytest -q
coverage report -m
```

Coverage settings live in `.coveragerc`.

## Code quality

Install the git hooks once:

```bash
pre-commit install
```

From then on, every commit runs the hooks in `.pre-commit-config.yaml`: whitespace and YAML checks, and a Black check that fails the commit if a file is not formatted (it reports the diff but does not change files).

## Concepts covered

- **ORM models** and how SQLAlchemy maps classes to tables.
- **Sessions and transactions**: `get_session()`, commit, rollback and `flush`.
- **Data access objects** that keep queries out of controllers and views.
- **Detached objects**: why values must be read inside the session block.
- **Form validation** with WTForms, and how form data reaches the model.
- **CSRF protection** with `CSRFProtect`, and why state changes use POST.
- **Testing**: unit tests with mocks, integration tests against a real database, route tests with Flask's test client, and branch coverage.

## Known limitations

- There is no authentication: anyone who can reach the application can change the data.
- Delete asks for no confirmation.
- Form field errors are shown only for the membership field.
- The Clear button only reloads the page.
