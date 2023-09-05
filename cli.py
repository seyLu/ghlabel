#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"


import typer

existing_usernames = ["rick", "morty"]


def maybe_create_user(username: str) -> None:
    if username == "root":
        print("The root user is reserved")
        raise typer.Abort()
    elif username in existing_usernames:
        print("The user already exists")
        raise typer.Exit(code=1)
    else:
        print(f"User created: {username}")


def send_new_user_notification(username: str) -> None:
    # Somehow send a notification here for the new user, maybe an email
    print(f"Notification sent for new user: {username}")


def main(username: str) -> None:
    maybe_create_user(username=username)
    send_new_user_notification(username=username)


if __name__ == "__main__":
    typer.run(main)
