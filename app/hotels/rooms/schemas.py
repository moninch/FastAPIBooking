

from pydantic import BaseModel


class RoomResponse(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    services: dict
    price: int
    quantity: int
    image_id: int
    total_cost: float
    rooms_left: int
    
    class Config:
            from_attributes = True