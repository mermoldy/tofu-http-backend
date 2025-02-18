# Tofu HTTP Backend

Implementation of the OpenTofu HTTP backend as part of the Scalr home assignment: <https://github.com/Scalr/home-assigment-tofu-http-backend>

## Setup the Project

- Install [uv](https://docs.astral.sh/uv/) and restart your shell:

```console
$~curl -LsSf https://astral.sh/uv/install.sh | sh
```

- Sync the dependencies:

```console
$~ uv sync
```

- Run the development HTTP server:

```console
$~ ./cli.py dev
```

## Automatic docs

The JSON Schemas of your models will be part of your OpenAPI generated schema, and will be shown in the interactive API docs at <http://127.0.0.1:8000/docs> adress.

## Run the tests

```console
$~ pytest
```

## Dev notes

- The structlog/uvicorn/fastapi configuration pattern is based on <https://gist.github.com/nymous/f138c7f06062b7c43c060bf03759c29e>.
