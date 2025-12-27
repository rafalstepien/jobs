# Jobs

## Goals
1. Aggregate job offers from main job boards in Poland
2. Expose common interface for filtering them and be able to filter in more detail (eg. `LOCATION=Wroclaw+Hybrid OR LOCATION=Remote`, `TECH_STACK=Python AND TECH_STACK=Rust`)


## Usage

```bash
make report
```

## Todo
Features
- request actual offers
- setup sending emails
- setup scheduler

Refactor
- Consider separating models exposed in API
- Handle pagination when there is a lot of offers
- Introduce criteria file (yaml/json) for filtering
- Dockerize
