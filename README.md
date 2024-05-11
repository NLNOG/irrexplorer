# IRR explorer: explore IRR & BGP data in near real time

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
  `https://bgp.tools/table.jsonl`.
* `BGP_SOURCE_MINIMUM_HITS`: the minimum number of hits a `BGP_SOURCE`
  record needs to be included. Default: 250.
* `RIRSTATS_URL_ARIN`, `RIRSTATS_URL_AFRINIC`, etc. URL for the 
  RIR stats file for each RIR (supports basic and extended format).
* `REGISTROBR_URL`: URL for the Registro.BR asn-blk file.
* `BGP_IPV4_LENGTH_CUTOFF` / `BGP_IPV6_LENGTH_CUTOFF`: BGP prefixes
  of this length or longer are dropped when importing BGP origin data.
  Default: 29 and 124.
* `MINIMUM_PREFIX_SIZE_IPV4` / `MINIMUM_PREFIX_SIZE_IPV6`: minimum prefix
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

### Development

For development, it can be helpful to run the uvicorn and react apps separately.
This also allow auto reloading.

* Activate the virtualenv, and run uvicorn with `uvicorn --reload irrexplorer.app:app`.
  This will listen on port 8000 by default and read settings from the `.env` file or
  environment as in production.
* Run the frontend from the frontend directory with `yarn start`. This will start
  a small webserver on port 3000. You need to set `REACT_APP_BACKEND` in the `.env`
  file to your local API URL.

To run tests, run `yarn build` (or `poetry run frontend-build`) at least once
(that build is used for static serving tests), activate the virtualenv,
then run `pytest`.

### Setting up a Development Environment with Docker Compose

To quickly set up your local infrastructure for development on your laptop using Docker containers, follow these three simple steps (assuming that you already have Docker and Docker-compose pre-installed):

```bash
# clone the repository
git clone git@github.com:NLNOG/irrexplorer.git`
# go to the dev directory
cd dev/
# start the development environment
docker-compose -f docker-up -d
```

After executing these steps, you will have all the necessary services up and running for development:
```bash
% docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS                    PORTS                                            NAMES
9b2ee198962f   dev-irrexplorer   "/app/irrexplorer/in…"   34 minutes ago   Up 33 minutes (healthy)   0.0.0.0:8000->8000/tcp                           irrexplorer
3b08fb5ba0c8   dev-irrd          "/app/irrd/init"         34 minutes ago   Up 33 minutes (healthy)   0.0.0.0:8043->8043/tcp, 0.0.0.0:8080->8080/tcp   irrd
67284918c7ea   postgres          "docker-entrypoint.s…"   34 minutes ago   Up 34 minutes (healthy)   5432/tcp                                         postgres_irre
c689fad6d0e9   postgres          "docker-entrypoint.s…"   34 minutes ago   Up 34 minutes (healthy)   5432/tcp                                         postgres_irrd
36414b39a412   redis             "docker-entrypoint.s…"   34 minutes ago   Up 34 minutes (healthy)   6379/tcp                                         redis_irrd
```

> You can can access IRR explorer web interface at http://localhost:8000/ and the API at http://localhost:8000/api/.

> IRRd web interface available at http://localhost:8080/.

> If you need to include or remove Routing Registries, check the file `irrd.yaml`/`sources`.

If you need to access the containers, use the following command:
```bash
docker exec -it <container_name> /bin/sh
```

Since uvicorn is running in the foreground, you can access the logs with:
```bash
docker logs -f irrexplorer
```

Uvicorn supports auto-reloading, making it easy to check changes. If a complete reload is required, simply run:
```bash
docker container restart irrexplorer
```

 Tail container logs:
```bash
docker-compose logs -f --tail 100
```


#### To streamline your development workflow, we have included several convenient `Make` commands:

`make clean`: Removes all unused Docker objects (containers, networks, volumes, and images) using `docker system prune --all`.

`make start`: Starts the Docker containers defined in the `docker-compose.yml` file using `docker-compose up -d`.

`make stop`: Stops and removes the Docker containers defined in the docker-compose.yml file using docker-compose down.

`make rebuild`: Executes the stop, clean, and start commands in sequence to rebuild the development environment.

`make dump_irrd_db`: Dumps the irrd database from the `postgres_irrd` container to a file named `irrdb.sql` using `docker exec` and `pg_dump`.

`make dump_irre_db`: Dumps the irrexplorer database from the `postgres_irre` container to a file named `irrexplorer_db.sql` using `docker exec` and `pg_dump`.

These commands provide a convenient way to manage the development environment, including starting, stopping, rebuilding, and dumping the databases.

#### The infrastructure includes the following components:

- PostgreSQL running for IRR Explorer using credentials specified in the docker-compose.yml;
- PostgreSQL running for IRRd using credentials specified in the docker-compose.yml;
- Redis used by IRRd;
- IRRd caching registry data, keeping it updated using NRTM, and serving this data to IRR Explorer;
- **Finally, IRR Explorer itself!**

Happy coding!
