#!/usr/bin/env python3
import click
import uvicorn
import uvicorn.logging


@click.group()
def cli() -> None:
    """The development helpers."""


@cli.command("dev")
def dev() -> None:
    """Run the development HTTP server via uvicorn."""
    uvicorn.run(
        "src.cmd:app", reload=True, log_config={"version": 1, "disable_existing_loggers": False}
    )


if __name__ == "__main__":
    cli()
