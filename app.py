import os
from flask import Flask, abort, redirect, render_template, url_for
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

from controllers.client_controller import (
    ClientNotFoundError,
    MembershipTakenError,
    delete_client,
    get_client,
    list_clients,
    save_client,
)
from forms.client_form import ClientForm
from models.client import Client

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["WTF_SECRET_KEY"]
csrf = CSRFProtect(app)
APP_TITLE = "Zona Fit (GYM)"


def render_index(client_form):
    clients = list_clients()
    context = {"app_title": APP_TITLE, "clients": clients, "client_form": client_form}
    return render_template("index.html", **context)


@app.route("/")
def index():
    return render_index(ClientForm(obj=Client()))


@app.route("/clean")
def clean():
    return redirect(url_for("index"))


@app.route("/edit/<int:client_id>")
def edit(client_id):
    client = get_client(client_id)
    if client is None:
        abort(404)
    return render_index(ClientForm(data=client))


@app.route("/save", methods=["GET", "POST"])
def save():
    client_form = ClientForm()
    if not client_form.validate_on_submit():
        return render_index(client_form)

    try:
        save_client(client_form.data)
    except MembershipTakenError:
        client_form.membership.errors.append("That membership already exists.")
        return render_index(client_form)
    except ClientNotFoundError:
        abort(404)
    return redirect(url_for("index"))


@app.route("/delete/<int:client_id>", methods=["POST"])
def delete(client_id):
    try:
        delete_client(client_id)
    except ClientNotFoundError:
        abort(404)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
