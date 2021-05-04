# IRR explorer: explore IRR & BGP data in near real time

[![CI](https://circleci.com/gh/dashcare/irrexplorer.svg?style=svg)](https://circleci.com/gh/dashcare/irrexplorer)

The first version of IRR explorer was written by
[Job Snijders](https://github.com/job/irrexplorer) to make it easier to debug
data in the IRR system. An example is to verify whether you would be impacted
by deployment of filtering strategies such as "IRR Lockdown".

The original project has several issues, and this IRR explorer v2 project
is an improved reimplementation on top of [IRRd](https://github.com/irrdnet/irrd)
for [Stichting NLNOG](https://nlnog.net/) by [DashCare BV](https://dashcare.nl/).


## Deployment

**DOCUMENTATION IN PROGRESS**

### Requirements

To run IRR explorer you need a Linux, BSD or MacOS install with:

* Python 3.7 or newer
* Poetry (package manager for Python)
* node
* yarn

You also need access to a PostgreSQL server, and a IRRd 4.2 deployment.

### Configuration

Create a file calle `.env` (where?) with content like:
```
DATABASE_URL=postgresql://localhost/irrexplorer
IRRD_ENDPOINT=https://irrd.as213279.net/graphql/
DEBUG=true
```

### Install

* As a non-privileged user, check out the git repository
* In the checkout, run `poetry install`, `poetry run frontend-install`, `poetry run frontend-build`, `poetry run alembic upgrade head`.

### Running

* `poetry run gunicorn -w 4 -k uvicorn.workers.UvicornWorker irrexplorer.app:app`
* `poetry run python irrexplorer/commands/import_data.py`
