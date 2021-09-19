from datetime import datetime, timedelta, timezone
from time import sleep

import dateutil.parser
import httpx
import telebot
import typer
from opset import config

from petfinderbot import utils

PETFINDER_BASE_URL = "https://api.petfinder.com/v2"


def get_petfinder_client():
    client = httpx.Client(base_url=PETFINDER_BASE_URL)

    token_resp = client.post(
        "/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": config.petfinder.client_id,
            "client_secret": config.petfinder.client_secret,
        },
    )
    token_resp.raise_for_status()

    client.headers = dict(authorization=f"Bearer {token_resp.json()['access_token']}", **client.headers)
    return client


def bot():
    telegram = telebot.TeleBot(config.telegram.token, parse_mode="MarkdownV2")
    typer.secho("Initialized Telegram client")

    last_check_time = datetime.now(timezone.utc)

    if config.debug.enabled:
        last_check_time -= timedelta(days=1)

    while True:
        typer.secho("Checking for new pets")

        search_filters = config.petfinder.filters or {}
        search_filters["sort"] = "recent"
        search_filters["after"] = last_check_time.isoformat()

        petfinder_client = get_petfinder_client()
        animals = []
        current_page = 0
        total_pages = 1
        while current_page < total_pages:
            search_filters["page"] = current_page + 1
            resp = petfinder_client.get("/animals", params=search_filters)

            if config.debug.enabled:
                print(resp.text)

            resp.raise_for_status()

            resp_data = resp.json()
            current_page = resp_data["pagination"]["current_page"]
            total_pages = resp_data["pagination"]["total_pages"]
            animals += resp_data["animals"]

        if not animals:
            typer.secho("No new pets found")
            sleep(config.sleep)
            continue

        last_check_time = dateutil.parser.parse(animals[0]["published_at"])

        reverse_order_pets = list(reversed(animals))

        for pet in reverse_order_pets:
            pet_country = pet["contact"]["address"]["country"]
            if config.petfinder.country_filter and pet_country != config.petfinder.country_filter:
                typer.secho("Ignoring pet not in Canada")
                continue

            pet_url = pet["url"]
            pet_name = pet["name"]
            pet_primary_breed = pet["breeds"]["primary"]
            pet_description = f"{pet['size']} {pet['age']} {pet['gender']}"

            typer.secho("New pet found!")

            telegram_pet_name = utils.escape_telegram_text(pet_name)
            telegram_pet_breed = utils.escape_telegram_text(pet_primary_breed)
            telegram_pet_description = utils.escape_telegram_text(pet_description)
            telegram_text = f"*[{telegram_pet_name}]({pet_url})*\n{telegram_pet_breed}\n{telegram_pet_description}"

            for chat_id in config.telegram.chat_ids:
                try:
                    telegram.send_message(chat_id, telegram_text)
                except Exception as e:
                    typer.secho(f"Error sending Telegram message: {str(e)}", fg="red")

            typer.secho("Telegram message sent!", fg="green")

        sleep(config.sleep)
