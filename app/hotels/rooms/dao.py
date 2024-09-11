from datetime import date
from typing import ClassVar, List

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms
from app.hotels.rooms.schemas import RoomResponse


class RoomsDAO(BaseModel):
    model: ClassVar = Rooms

    @classmethod
    async def find_all(cls, hotel_id: int, date_from: date, date_to: date) -> List[RoomResponse]:
        async with async_session_maker() as session:
            booked_rooms = select(
                Bookings.room_id,
                func.count(Bookings.room_id).label('booked_count')
            ).where(
                or_(
                    and_(Bookings.date_from >= date_from, Bookings.date_from <= date_to),
                    and_(Bookings.date_from <= date_from, Bookings.date_to > date_from)
                )
            ).group_by(Bookings.room_id).cte('booked_rooms')

            total_days = (date_to - date_from).days

            rooms_query = select(
                Rooms.id.label('room_id'),
                Rooms.hotel_id,
                Rooms.name.label('room_name'),
                Rooms.description,
                Rooms.serviсes,
                Rooms.price,
                Rooms.quantity,
                Rooms.image_id,
                (Rooms.price * total_days).label('total_cost'),
                (Rooms.quantity - func.coalesce(booked_rooms.c.booked_count, 0)).label('rooms_left')
            ).outerjoin(
                booked_rooms, Rooms.id == booked_rooms.c.room_id
            ).filter(
                Rooms.hotel_id == hotel_id
            )

            result = await session.execute(rooms_query)
            rooms = result.all()

            if not rooms:
                raise HTTPException(status_code=404, detail="Rooms not found")

            return [
                RoomResponse(
                    id=room.room_id,
                    hotel_id=room.hotel_id,
                    name=room.room_name,
                    description=room.description,
                    services=room.serviсes if isinstance(room.serviсes, dict) else {},
                    price=room.price,
                    quantity=room.quantity,
                    image_id=room.image_id,
                    total_cost=room.total_cost,
                    rooms_left=room.rooms_left
                )
                for room in rooms
            ]