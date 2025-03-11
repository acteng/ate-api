from fastapi import Depends, FastAPI

from ate_api import example
from ate_api.auth import authorize

app = FastAPI(dependencies=[Depends(authorize)])
app.include_router(example.router)
