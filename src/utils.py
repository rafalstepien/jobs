from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
from yarl import URL

from models.domain import WebsiteOkResponse


def open_html(name: str) -> str:
    with open(Path(__file__).parent.parent / "sample_responses" / f"{name}.html") as html_file:
        return html_file.read()


def get_offers_html() -> list[WebsiteOkResponse]:
    return [
        WebsiteOkResponse(
            html=open_html("single_offer_rust"),
            url=URL("https://justjoin.it/job-offer/air-space-intelligence-software-engineer-gdansk-python-e10b493e"),
        ),
        WebsiteOkResponse(
            html=open_html("single_offer_rust2"),
            url=URL("https://justjoin.it/job-offer/hyperexponential-senior-software-engineer-rust--warszawa-python"),
        ),
        WebsiteOkResponse(
            html=open_html("single_offer_multiple_cities"),
            url=URL(
                "https://justjoin.it/job-offer/grid-dynamics-poland-senior-full-stack-developer-python-typescript--warszawa-python"
            ),
        ),
    ]


def prepare_jinja_env(template_filename: str) -> Template:
    jinja_env = Environment(loader=FileSystemLoader(searchpath=Path(__file__).parent / "templates"))
    jinja_env.filters["format_number"] = format_number
    return jinja_env.get_template(template_filename)


def format_number(value: str) -> str:
    """
    Jinja2 filter to display thousands nicely
    """
    return f"{value:,}"


def save_report(report, output_filename: str) -> None:
    with open(output_filename, "w") as f:
        f.write(report)
