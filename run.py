import typer
from opset import setup_config

from petfinderbot import bot

setup_config("petfinderbot", "petfinderbot.config")
cli = typer.Typer()


@cli.command()
def main():
    typer.secho("Starting PetFinder bot", fg="blue")
    bot.bot()


if __name__ == '__main__':
    cli()
