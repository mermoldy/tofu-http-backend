import sys

import dotenv
import fastapi
import pydantic_core

from src import config
from src import log
from src import middlewares
from src.app import state

dotenv.load_dotenv()

try:
    config.get_config()
except pydantic_core.ValidationError as err:
    print("Errors occurred while loading the application config:")
    for e in err.errors():
        print(f" - {e['loc'][0]}: {e['msg']}")
    print("Please configure the application via config.toml file and restart the HTTP server.")
    sys.exit(1)

log.setup_logging(level=config.config.log_level)

LOG = log.get_logger(__name__)
LOG.info("Starting HTTP backend.")

app = fastapi.FastAPI()
app.add_middleware(middlewares.LogMiddleware)
app.include_router(state.api.router)
