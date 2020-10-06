import click


@click.command()
@click.option("--tgtoken", envvar="TG_TOKEN")
@click.option("--dburl", envvar="DATABASE_URL", default="sqlite:///database.sqlite")
@click.option("--walnut", default=None)
def run(tgtoken, dburl, walnut):
    # pylint: disable=import-outside-toplevel
    from expenses import const

    const.DATABASE_URL = dburl
    const.TG_TOKEN = tgtoken
    if walnut is not None:
        from expenses.walnut import import_walnut_report

        import_walnut_report(walnut)
    else:
        from expenses.bot import runbot

        runbot()


run()  # pylint: disable=no-value-for-parameter
