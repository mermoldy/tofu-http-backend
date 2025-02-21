# Tofu HTTP Backend

Implementation of the OpenTofu HTTP backend as part of the Scalr home assignment: <https://github.com/Scalr/home-assigment-tofu-http-backend>

- [Design](#design)
- [Setup](#setup)
- [Development](#development)
- [Testing](#testing)
- [API documentation](#api-documentation)
- [Usage example](#usage-example)
- [Usage example](#usage-example)

## Design

The application core is built using the [FastAPI](https://fastapi.tiangolo.com/) asyncio server with the [Uvicorn ASGI](https://www.uvicorn.org/) server. Logging is handled using the [structlog](https://www.structlog.org/en/stable/) protocol, and testing is implemented with [pytest](https://docs.pytest.org/en/stable/) framework. [MinIO](https://github.com/minio/minio) is used as an example for both storage and the lock backend.

The application layout follows the [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) pattern.
The configuration is located in [config.toml](./config.toml) and also supports loading properties from shell variables prefixed with `TOFU_HTTP_<UPPERCASE_KEY>`.

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

## Development

Run the development HTTP server with hot-reload:

```console
$~ ./cli.py dev
```

The application entrypoint is placed at [src/cmd.py](src/cmd.py) module.
By default, the application runs on port 8000.

## Build

Use `uv pip compile pyproject.toml` to compile the production dependencies.

Then, run `docker build . -t tofu-http-server:latest` to build the Docker image, and `docker run -it tofu-http-server:latest` to start the container.

## Testing

```console
$~ pytest
```

see [tests](./tests/) for more.

## API documentation

API Documentation

The interactive API documentation is built using FastAPI and is available at <http://127.0.0.1:8000/docs>.

## Configuration Parameters

The table below outlines the configuration options for the application.

| Parameter          | Type                  | Default Value                                  | Description |
|-------------------|----------------------|--------------------------------|-------------|
| `log_level`      | `str`                 | `"info"`                     | The log level. |
| `username`       | `str \| None`         | `None`                        | The username for HTTP basic authentication. |
| `password`       | `str \| None`         | `None`                        | The password for HTTP basic authentication. |
| `storage_backend` | `"minio"`            | `"minio"`                     | The remote storage backend used for storing state files. |
| `lock_backend`    | `"minio"`            | `"minio"`                     | The remote storage backend used for state file locking. |
| `minio_host`      | `str`                 | `"play.min.io"`               | The MinIO host. |
| `minio_bucket`    | `str`                 | `"e1cc89bb-b9f5-4b29-8163-c3e8da21bbba"` | The bucket in MinIO storage. |
| `minio_access_key` | `str`                | _Required_                     | The MinIO access key. |
| `minio_secret_key` | `str`                | _Required_                     | The MinIO private secret key. |

> [!TIP]
> All configuration properties can also be loaded from environment variables by using the `TOFU_HTTP_<UPPERCASE_KEY>` prefix.

For example:

```sh
export TOFU_HTTP_MINIO_HOST="my-minio.example.com"
```

## Usage example

Add the following http backend configuration to your main.tf file:

```hcl
terraform {
  backend "http" {
    address        = "http://localhost:8000/state/project/1"
    lock_address   = "http://localhost:8000/state/lock/project/1"
    unlock_address = "http://localhost:8000/state/unlock/project/1"
    lock_method    = "POST"
    unlock_method  = "POST"
    username       = "testscalr"
    password       = "testscalr"
  }
}
```

Run the server using Docker with the following command, using the pre-built image:

```console
$~ docker run -it -p 8000:8000 -e TOFU_HTTP_USERNAME=testscalr -e TOFU_HTTP_PASSWORD=testscalr mermoldy/tofu-http-server:0.1.0
```
