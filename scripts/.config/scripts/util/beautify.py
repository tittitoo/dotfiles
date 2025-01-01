"For beautifying excel files based on given template"

import click

TEMPLATE = [
    "modec-commissioning-spares",
    "modec-2yrs-spares",
    "spl-cq-form",
]


@click.command()
def beautify():
    "Beautify excel file based on template"
    click.echo("The following templates are available:")
    for index, template in enumerate(TEMPLATE, start=1):
        click.echo(f"{index}: {template}")
    template_number = click.prompt("Type the template number", type=int)
    file = click.prompt("Choose the file name")
    click.echo(f"{template_number}, {file}")


def test():
    pass
