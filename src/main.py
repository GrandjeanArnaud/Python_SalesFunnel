"""Application entrypoint wiring FastAPI routers.

This module creates the FastAPI `app` and includes routers defined in
`src.controllers`. It intentionally keeps startup logic minimal so tests
can import `app` without side-effects.
"""

from src import controllers
from fastapi import FastAPI

app = FastAPI()

# Register routers defined under src.controllers
app.include_router(controllers.interest_router)
app.include_router(controllers.workflow_router)
