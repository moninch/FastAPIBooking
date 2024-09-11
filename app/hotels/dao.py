from datetime import date

from sqlalchemy import and_, func, or_, select, text

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.hotels.schemas import SHotelResponse


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location, date_from: date, date_to: date):

        async with async_session_maker() as session:
            booked_rooms = (
                select(
                    Bookings.room_id, func.count(Bookings.room_id).label("booked_count")
                )
                .where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to,
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from,
                        ),
                    )
                )
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )

            rooms_per_hotel = (
                select(Rooms.hotel_id, func.count(Rooms.id).label("rooms_total"))
                .group_by(Rooms.hotel_id)
                .cte("rooms_per_hotel")
            )

            available_hotels_query = (
                select(
                    Hotels.id.label("hotel_id"),
                    Hotels.name.label("hotel_name"),
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (
                        func.sum(Rooms.quantity)
                        - func.coalesce(func.sum(booked_rooms.c.booked_count), 0)
                    ).label("rooms_left"),
                )
                .join(Rooms, Rooms.hotel_id == Hotels.id)
                .outerjoin(booked_rooms, Rooms.id == booked_rooms.c.room_id)
                .filter(
                    text(
                        f"to_tsvector('russian', location) @@ plainto_tsquery('russian', '{location}')"
                    )
                )
                .group_by(Hotels.id)
                .having(
                    (
                        func.sum(Rooms.quantity)
                        - func.coalesce(func.sum(booked_rooms.c.booked_count), 0)
                    )
                    > 0
                )
            )

            result = await session.execute(available_hotels_query)
            hotels = result.fetchall()
            return [
                {
                    "id": hotel.hotel_id,
                    "name": hotel.hotel_name,
                    "location": hotel.location,
                    "services": hotel.services,
                    "rooms_quantity": hotel.rooms_quantity,
                    "image_id": hotel.image_id,
                    "rooms_left": hotel.rooms_left,
                }
                for hotel in hotels
            ]
