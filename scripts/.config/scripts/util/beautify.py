"For beautifying excel files based on given template"

import click

TEMPLATE = [
    "General",
    "MODEC Commissioning Spares",
    "MODEC 2YRS Spares",
    "Seatrium CQ Form",
]


@click.command()
def beautify():
    "Beautify excel file based on template."
    click.echo("The following templates are available:")
    templates = {index: value for index, value in enumerate(TEMPLATE, start=1)}
    for index, template in templates.items():
        click.echo(f"{index}: {template}")
    while True:
        template_number = click.prompt("Type the template number or q to quit")
        try:
            if int(template_number) in templates.keys():
                template_number = int(template_number)
                break
        except ValueError:
            if template_number.lower() == "q":
                return
        click.echo("Not a valid value.")
    file = click.prompt("The file name in the current directory")
    click.echo(f"{templates[template_number]}, {file}")
    match templates[template_number]:
        case "General":
            click.echo("General")
        case "MODEC Commissioning Spares":
            click.echo("MODEC Commissioning Spares")
        case "MODEC 2YRS Spares":
            click.echo("MODEC 2YRS Spares")
        case "Seatrium CQ Form":
            click.echo("Seatrium CQ Form")
        case _:
            click.echo("Invalid template")


if __name__ == "__main__":
    beautify()
