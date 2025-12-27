# Jobs

## Goals
1. Aggregate job offers from main job boards in Poland
2. Expose common interface for filtering them and be able to filter in more detail (eg. `LOCATION=Wroclaw+Hybrid OR LOCATION=Remote`, `TECH_STACK=Python AND TECH_STACK=Rust`)
3. Receive email reports on daily/weekly basis


## Usage

```bash
make report
```


## Example
```python
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
```
The above criteria say:
- Tech stack must include both Python and Rust
- Location must be remote, or hybrid in Warsaw, or hybrid in Gdansk

And produce the following example report:
![example_report](./example_report.png)

## Tasks
Features
- request actual offers instead of preloading them from local responses
- setup sending emails
- setup daily/weekly scheduler
- highlight the tech stack badges matching filters

Refactor
- Use cache
- Prepare for production:
    - docker (non-root user)
- Introduce criteria file (yaml/json) for filtering
- Deploy to the could: 
    - Render:
        - Deploy via dashboard by pasting image URL and setting port, done in 2 minutes. 
        - Free tier = 750h / month
        - spins down after 15 min idle
        - cron jobs via dashboard
    - fly.io: 
        - One command deploy
        - free tier: 3 shared VMs, 100k reqs/month
        - scheduling little bit more complicated than in Render
    - Oracle Cloud Always Free:
        - Free tier includes: 4 OCPUs (8vCPUs) + 24GB RAM machine with 3k OCPU hours and 18k GB hours / month
        - 4-OCPU VM running 24/7 for ~31 days uses 4 × 24 × 31 = 2,976 hours
        - GB hours track RAM: 24GB VM 24/7 for ~31 days = 24 × 24 × 31 = 17,856 hours—under 18,000
        - Can install cron and use cron jobs.
- Consider separating models exposed in API

Bugfix:
- Better error handling
- Handle pagination when there is a lot of offers
