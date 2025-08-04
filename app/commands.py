import click
from flask.cli import with_appcontext
from app.models import *
from app.constant import Regex
from faker import Faker
from app.extensions import db
import re

fake = Faker()

@click.command("seed-db")
@with_appcontext
def seed_db():
    for _ in range(50):
        try:
            reservation = Reservation(
                check_in = fake.date_time(),
                check_out = fake.date_time(),
                guest_count = fake.random_digit(),
                fullname = fake.name_male(),
                email = fake.email(),
                phone_number = fake.basic_phone_number(),
                room_id = 1
            )
            db.session.add(reservation)
            db.session.commit()
        except Exception as err:
            print(err)
            continue

    click.echo("Database seeded.")

def validate_username_unique(username):
    if not re.match(Regex.USERNAME, username):
        raise click.BadParameter("Invalid format.")
    if Admin.query.filter_by(username=username).first():
        raise click.BadParameter("Username already taken.")
    return username


@click.command("seed-admin")
@with_appcontext
def seed_admin():
    """Seed an initial admin user."""
    fullname = click.prompt("Full Name")
    username = click.prompt("Username", value_proc=validate_username_unique)
    password = click.prompt(
        "Admin password", 
        hide_input=True, 
        confirmation_prompt=True
    )

    # Check if admin already exists
    if Admin.query.filter_by(username=username).first():
        click.echo("Admin user already exists with that username.")
        return

    user = Admin(
        fullname=fullname,
        username=username,
        password=password, 
    )
    db.session.add(user)
    db.session.commit()
    click.echo(f"✅ New admin '{user.username}' added.")


@click.command("reset-db")
@with_appcontext
def reset_db():
    db.drop_all()
    db.create_all()
    click.echo("✅ Database reset.")

@click.command("drop-db")
@with_appcontext
def drop_db():
    db.drop_all()
    click.echo("✅ Database dropped.")
