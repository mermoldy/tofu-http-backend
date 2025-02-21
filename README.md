# Tofu HTTP Backend

Implementation of the OpenTofu HTTP backend as part of the Scalr home assignment: <https://github.com/Scalr/home-assigment-tofu-http-backend>

- [Design](#design)
- [Setup](#setup)
- [Testing](#testing)
- [API documentation](#api-documentation)
- [Example configuration](#example-configuration)

## Design

The application core is built using the [FastAPI](https://fastapi.tiangolo.com/) asyncio server with the [Uvicorn ASGI](https://www.uvicorn.org/) server. Logging is handled using the [structlog](https://www.structlog.org/en/stable/) protocol, and testing is implemented with pytest. [MinIO](https://github.com/minio/minio) is used as an example for both storage and the lock backend.

The application layout follows the [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) pattern.
The configuration is located in [config.toml](./config.toml).

> [!WARNING]
> Since MinIO does not natively support locking, the lock backend implements a simple mechanism by placing a `.lock` file with metadata in storage alongside the main blob file. However, this approach may not be sufficient for high-concurrency applications, as it can lead to collisions or race conditions. It is provided solely as an example.

## Setup

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

## Testing

```console
$~ pytest
```

see [tests](./tests/) for more.

## API documentation

API Documentation

The interactive API documentation is built using FastAPI and is available at <http://127.0.0.1:8000/docs>.

## Example configuration

Add the following http backend configuration to your main.tf file:

```hcl
terraform {
  backend "http" {
    address        = "http://localhost:8000/state/project/1"
    lock_address   = "http://localhost:8000/state/lock/project/1"
    unlock_address = "http://localhost:8000/state/unlock/project/1"
    lock_method    = "POST"
    unlock_method  = "POST"
    username       = "scalr"
    password       = "scalr"
  }
}
```

Update the username and password in [config.toml](./config.toml) , then start the HTTP backend application using `./cli.py dev`.
