import click
from datetime import datetime

from criteria import CriteriaRule, LocationCriteria, LocationKeyword, TechCriteria, TechKeyword
from jjit_board_parser import JJITBoardParser
from utils import load_jinja_template


@click.group()
def main():
    """A simple CLI tool to manage reports."""
    pass


@main.command()
# TODO: @click.option('--criteria-file', default='Standard', help='The name of the report.') 
@click.option('--output-file-name', default='jobs_report', help='The name of the file that will be produced as output without extension.')
def generate(
    output_file_name: str
):
    criteria = [
        TechCriteria(
            keywords=[TechKeyword(name="Rust"), TechKeyword(name="Python")],
            rule=CriteriaRule.ALL,
        ),
        LocationCriteria(
            keywords=[
                LocationKeyword(form="hybrid", city="gdansk"),
                LocationKeyword(form="hybrid", city="wroclaw"),
                LocationKeyword(form="hybrid", city="warszawa"),
                LocationKeyword(form="remote"),
            ],
            rule=CriteriaRule.AT_LEAST_ONE,
        ),
    ]

    jobs = JJITBoardParser().find_offers(criteria)
    template = load_jinja_template("report_template_jinja")
    html_output = template.render(jobs=jobs, report_date=datetime.now().strftime("%B %d, %Y"))

    output_file_path = f"{output_file_name}.html"
    with open(output_file_path, "w") as f:
        f.write(html_output)
    
    click.secho(f"Report saved as {output_file_path}", fg='green')


if __name__ == '__main__':
    main()