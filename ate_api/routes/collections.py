from ate_api.routes.base import BaseModel


class CollectionModel[T](BaseModel):
    items: list[T]
