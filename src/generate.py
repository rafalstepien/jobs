# import click
import asyncio
from datetime import datetime

from criteria import CriteriaRule, LocationCriteria, LocationKeyword, TechCriteria, TechKeyword
from jjit_api_client import JJITAPIClient
from jjit_board_parser import JJITBoardParser
from utils import prepare_jinja_env, save_report

# @click.group()
# def main():
#     """A simple CLI tool to manage reports."""
#     pass


# @main.command()
# @click.option(
#     "--output-file-name",
#     default="jobs_report.html",
#     help="The name of the file that will be produced as output",
# )
async def generate(output_file_name: str):
    criteria = [
        TechCriteria(
            keywords=[TechKeyword(name="Rust"), TechKeyword(name="Python")],
            rule=CriteriaRule.ALL,
        ),
        LocationCriteria(
            keywords=[
                LocationKeyword(form="hybrid", city="gdansk"),
                LocationKeyword(form="hybrid", city="warszawa"),
                LocationKeyword(form="remote"),
            ],
            rule=CriteriaRule.AT_LEAST_ONE,
        ),
    ]
    jjit_api_client = JJITAPIClient()
    parser = JJITBoardParser(jjit_api_client)
    jobs = await parser.find_offers(criteria)
    template = prepare_jinja_env("report.html")
    report = template.render(jobs=jobs, report_date=datetime.now().strftime("%B %d, %Y"))
    save_report(report, output_file_name)
    # click.secho(f"Report saved as {output_file_name}", fg="green")
    print(f"Report saved as {output_file_name}")


if __name__ == "__main__":
    asyncio.run(generate("jobs_report.html"))
