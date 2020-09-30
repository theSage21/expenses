import click
from expenses.bot import runbot


@click.command()
def run():
    runbot()
