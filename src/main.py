from datetime import datetime
from src import controllers
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI

app = FastAPI()

# template = Jinja2Templates(directory='src/templates')

app.include_router(controllers.interest_router)
app.include_router(controllers.workflow_router)

print("Routers added to the FastAPI application.")
