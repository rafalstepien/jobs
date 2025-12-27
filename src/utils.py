from pathlib import Path

from jinja2 import Template


def open_html(name: str) -> str:
    with open(Path(__file__).parent.parent / "sample_responses" / f"{name}.html", "r") as html_file:
        return html_file.read()


def load_jinja_template(name: str) -> Template:
    with open(Path(__file__).parent / "templates" / f"{name}.html", "r") as f:
        return Template(f.read())
