import asyncio
from datetime import date
from typing import List

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache
from pydantic import TypeAdapter

from app.hotels.dao import HotelDAO
from app.hotels.rooms.schemas import RoomResponse
from app.hotels.schemas import SHotelResponse

router = APIRouter(
    prefix="/hotels",
    tags =["Отели"],
)

@router.get("/{location}")
@cache(expire=30)
async def get_hotels(
    location: str,
    date_from: date = Query(..., description=f"Например 2023-05-15"),
    date_to: date = Query(..., description=f"Например 2023-06-20")
    ) -> List[SHotelResponse]:
    hotels = await HotelDAO.find_all(location,date_from,date_to)
    return hotels

@router.get("/id/{hotel_id}")
async def get_hotels_by_id(hotel_id: int):
    return await HotelDAO.find_by_id(hotel_id)
