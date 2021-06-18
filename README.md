# IRR explorer: explore IRR & BGP data in near real time

[![CI](https://circleci.com/gh/dashcare/irrexplorer.svg?style=svg)](https://circleci.com/gh/dashcare/irrexplorer)

The first version of IRR explorer was written by
[Job Snijders](https://github.com/job/irrexplorer) to make it easier to debug
data in the IRR system. An example is to verify whether you would be impacted
by deployment of filtering strategies such as "IRR Lockdown".

The original project has several issues, and this IRR explorer v2 project
is an improved reimplementation on top of [IRRd](https://github.com/irrdnet/irrd)
for [Stichting NLNOG](https://nlnog.net/) by [DashCare BV](https://dashcare.nl/).


## Data sources

Queried from an [IRRd 4.2+ instance](https://irrd.readthedocs.io/):

* IRR objects and relations (route(6) and as-sets)
* RPKI ROAs and the validation status of route(6) objects
  
Loaded into a local PostgreSQL database periodically:
  
* BGP origins for prefixes in the DFZ
* [RIRstats](https://www.apnic.net/about-apnic/corporate-documents/documents/resource-guidelines/rir-statistics-exchange-format/)


## Deployment

IRR explorer consists of a Python backend, based on
[Uvicorn](https://www.uvicorn.org/) and [Starlette](https://www.starlette.io/).
This backend provides a JSON API. The frontend is ReactJS.

By default, the backend also serves the static files of the frontend. These
static files are built during installation. Therefore,
you only need to start one Python HTTP process. Technically, it might be more
efficient to serve the frontend separately from a CDN, or at least to skip the
path through the Python backend. However, the frontend is small and entirely
cacheable, which is why this readme uses the simplest option.

The Python backend is async, which means
a single Python worker can serve multiple clients at the same time, while waiting
on results from backends.

### Requirements

To run IRR explorer you need a Linux, BSD or MacOS install with:

* Python 3.7 or newer
* Poetry (package manager for Python)
* node (tested on version 15 and 16)
* yarn

You also need access to a PostgreSQL server, and an IRRd 4.2+ deployment.

### Configuration

There are two ways to configure IRRexplorer:

* Set the config in environment variables. You should ensure these environment
  variables are set every time you run a command through `poetry`.
* Create a `.env` file in the git checkout created during the install step,
  and store the settings in this file.

The required settings are:

* `DATABASE_URL`: the URL of the PostgreSQL database, e.g.
  `postgresql://localhost/irrexplorer` to connect
  to the local database `irrexplorer` over a unix socket. 
  Only PostgreSQL is supported.
* `IRRD_ENDPOINT`: the URL of the IRRd 4.2+ GraphQL endpoint, e.g.
  `https://irrd.example.net/graphql/`.
  
You can optionally set:

* `HTTP_PORT`: the local HTTP port to bind to. Only used by the
  `poetry run http` command. Default: 8000.
* `HTTP_WORKERS`: the number of HTTP workers to start. Only used by the
  `poetry run http` command. Default: 4.
* `DEBUG`: enables debug mode in the web server. defaults to `False`.
  Do not enable in production.
* `BGP_SOURCE`: the source of BGP origin information. Default:
  `http://lg01.infra.ring.nlnog.net/table.txt`
* `RIRSTATS_URL_ARIN`, `RIRSTATS_URL_AFRINIC`, etc. URL for the 
  RIR stats file for each RIR (supports basic and extended format).
* `BGP_IPV4_LENGTH_CUTOFF` / `BGP_IPV6_LENGTH_CUTOFF`: BGP prefixes
  of this length or longer are dropped when importing BGP origin data.
  Default: 29 and 124.
* `MINIMUM_PREFIX_SIZE_IPV4` / `MINIMUM_PREFIX_SIZE_IPV4`: minimum prefix
  length for queries. Prefixes shorter than this are rejected, to limit
  database load. Default: 9 and 29.


If you choose to create a `.env` file, it should look similar to:
```
DATABASE_URL=postgresql://localhost/irrexplorer
IRRD_ENDPOINT=https://irrd.example.net/graphql/
```

### Install

* As a non-privileged user, check out the git repository
* In the checkout, run
  * `poetry install`, to install Python dependencies
  * `poetry run frontend-install`, to install javascript dependencies
  * `poetry run frontend-build`, to make a local production build of the frontend
  * `poetry run alembic upgrade head`, to create the database schema
    
To update a local install, update your local checkout, then run the steps
above again - they are aware of existing state and safe to execute multiple
times.

Poetry is a Python package manager that automatically creates and manages a
virtual environment. You can get more details about the virtual environment
poetry is using with `poetry env info`.

### Running

To run IRR explorer, you need to run the periodic data importer and an HTTP server.

The periodic data importer is run as `poetry run import-data`. This updates the local
BGP and RIR stats data. You should schedule this to run regularly, e.g. in a cronjob.
It can take around 15-20 minutes to complete.

The simplest way to run the HTTP server is with `poetry run http`. This starts the
HTTP listener in the foreground. It will always bind to localhost, and you can set
the local port and number of workers with the `HTTP_PORT` and `HTTP_WORKERS` settings.

For more advanced deployments, see the
[Uvicorn deployment documentation](https://www.uvicorn.org/deployment/#using-a-process-manager).
The app name for IRR explorer is `irrexplorer.app:app`. 
