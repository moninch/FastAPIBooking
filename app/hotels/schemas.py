from typing import Optional

from pydantic import BaseModel


class SHotelResponse(BaseModel):
        id: int
        name: str
        location: str
        services: Optional[list]
        rooms_quantity: int
        image_id: Optional[int]
        rooms_left: int

        class Config:
            from_attributes = True