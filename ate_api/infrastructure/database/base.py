from enum import Enum

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase


class BaseEntity(DeclarativeBase):
    type_annotation_map = {
        Enum: sqlalchemy.Enum(
            Enum,
            native_enum=False,
            # Persist enum value instead of name
            values_callable=lambda enums: [enum.value for enum in enums],
        )
    }
