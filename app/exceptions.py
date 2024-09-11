from fastapi import HTTPException, Response, status

UserAlreadyExistsException = HTTPException(
    status_code= status.HTTP_409_CONFLICT,
    detail= 'Пользователь уже зарегистрирован'
)

IncorrectEmailOrPasswordException = HTTPException(
    status_code= status.HTTP_401_UNAUTHORIZED,
    detail="Неправильная почта или пароль"
                                                  )

TokenExpireException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Срок действия токена истек'
    )

TokenAbsentException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                                     ,detail='Токена истек')

UserIsNotPresentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    )

RoomCanNotBeBookedException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail= "Не осталось свободных номеров"
    )