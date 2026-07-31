from collections.abc import Mapping
from enum import Enum
from typing import Any

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.type_api import TypeEngine


class BaseEntity(DeclarativeBase):
    type_annotation_map: Mapping[Any, TypeEngine[Any]] = {
        Enum: sqlalchemy.Enum(
            Enum,
            native_enum=False,
            # Persist enum value instead of name
            values_callable=lambda enums: [enum.value for enum in enums],
        )
    }
