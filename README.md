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

## Locking

The backend uses POST method types for locking:

Example configuration:

```hcl
terraform {
  backend "http" {
    address        = "http://localhost:8000/state/project/1"
    lock_address   = "http://localhost:8000/state/lock/project/1"
    unlock_address = "http://localhost:8000/state/unlock/project/1"
    lock_method    = "POST"
    unlock_method  = "POST"
  }
}
```

Since MinIO does not natively support locking, this lock backend uses a simple
mechanism by placing a `.lock` file with metadata in storage alongside the main blob file.
However, this approach may not be sufficient for high-concurrency applications,
as it can lead to collisions or race conditions.

For production-ready locking, a backend that natively supports locks should be used.

## Dev notes

- The structlog/uvicorn/fastapi configuration pattern is based on <https://gist.github.com/nymous/f138c7f06062b7c43c060bf03759c29e>.

## Plan

- Implement basic auth.
- Add more tests and docs for tesing
- Finalize docs and add some examples.
- Final review and testing.
