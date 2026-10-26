from werkzeug.datastructures import MultiDict

from forms.client_form import ClientForm


def make_form(app, **data):
    with app.test_request_context("/save", method="POST"):
        return ClientForm(formdata=MultiDict(data), meta={"csrf": False})


def test_valid_data_passes(app):
    form = make_form(app, first_name="Ana", last_name="Lopez", membership="10")

    assert form.validate() is True


def test_required_fields_are_enforced(app):
    form = make_form(app, first_name="", last_name="", membership="")

    assert form.validate() is False
    assert "first_name" in form.errors
    assert "last_name" in form.errors
    assert "membership" in form.errors


def test_membership_cannot_be_negative(app):
    form = make_form(app, first_name="Ana", last_name="Lopez", membership="-1")

    assert form.validate() is False
    assert "membership" in form.errors


def test_names_are_limited_to_50_characters(app):
    form = make_form(app, first_name="x" * 51, last_name="Lopez", membership="10")

    assert form.validate() is False
    assert "first_name" in form.errors
