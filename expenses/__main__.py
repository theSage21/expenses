import click


@click.command()
@click.option("--tgtoken", envvar="TG_TOKEN")
@click.option("--dburl", envvar="DATABASE_URL", default="sqlite:///:memory:")
def run(tgtoken, dburl):
    from expenses import const

    const.DATABASE_URL = dburl
    const.TG_TOKEN = tgtoken
    from expenses.bot import runbot

    runbot()
