from fastapi import FastAPI

from ate_api import example

app = FastAPI()
app.include_router(example.router)
