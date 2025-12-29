import asyncio
from datetime import datetime

from criteria import LocationCriteria, LocationKeyword, LocationRule
from jjit_api_client import JJITAPIClient
from jjit_board_parser import JJITBoardParser
from models import ProgrammingLanguage
from utils import prepare_jinja_env, save_report


async def generate(output_file_name: str):
    language = ProgrammingLanguage.PYTHON
    include_skills = ["Python", "Docker"]
    location_criteria = [
        LocationCriteria(
            keywords=[
                LocationKeyword(form="hybrid", city="wroclaw"),
                LocationKeyword(form="remote"),
            ],
            rule=LocationRule.AT_LEAST_ONE,
        ),
    ]
    jjit_api_client = JJITAPIClient()
    parser = JJITBoardParser(jjit_api_client)

    jobs = await parser.find_offers(include_skills, location_criteria, language)
    template = prepare_jinja_env("report.html")
    report = template.render(jobs=jobs, report_date=datetime.now().strftime("%B %d, %Y"))

    save_report(report, output_file_name)
    print(f"Report saved as {output_file_name}")


if __name__ == "__main__":
    asyncio.run(generate("jobs_report.html"), debug=True)
