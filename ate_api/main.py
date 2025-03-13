from fastapi import Depends, FastAPI

from ate_api import example
from ate_api.auth import bearer_scheme

app = FastAPI(dependencies=[Depends(bearer_scheme)])
app.include_router(example.router)
