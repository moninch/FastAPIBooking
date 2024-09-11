from datetime import date

from fastapi import APIRouter, Depends, Request
from pydantic import TypeAdapter
from sqlalchemy import select

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.database import async_session_maker
from app.exceptions import RoomCanNotBeBookedException
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users
from fastapi_versioning import version
router = APIRouter(
    prefix="/bookings",
    tags =["Bookings"],
)

@router.get("")
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all(user_id = user.id)

@router.delete("/{booking_id}")
@version(1)
async def delete_bookings(booking_id: int, user: Users = Depends(get_current_user)):
    return await BookingDAO.delete_model(booking_id)

@router.post("")
@version(1)
async def add_booking(room_id:int , date_from: date , date_to: date,user: Users = Depends(get_current_user)):
    booking = await BookingDAO.add(user.id, room_id,date_from,date_to)
    if not booking:
        raise RoomCanNotBeBookedException
    ta = TypeAdapter(SBooking)
    booking_dict = ta.validate_python(booking).model_dump()
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict
    