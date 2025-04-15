from pydantic import BaseModel


class CollectionModel[T](BaseModel):
    items: list[T]
