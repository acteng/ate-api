from fastapi import Depends, FastAPI

from ate_api import authorities
from ate_api.auth import authorize

app = FastAPI(
    title="ATE API",
    description="The Active Travel England Web API.",
    dependencies=[Depends(authorize)],
)
app.include_router(authorities.router)
