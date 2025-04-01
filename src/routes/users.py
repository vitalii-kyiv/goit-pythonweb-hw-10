from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from sqlalchemy.ext.asyncio import AsyncSession

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.conf.config import settings
from src.core.depend_service import get_auth_service, get_user_service, get_current_user
from src.core.email_token import get_email_from_token
from src.database.db import get_db
from src.entity.models import User
from src.schemas.email import RequestEmail
from src.schemas.user import UserResponse
from src.services.auth import AuthService, oauth2_scheme
from src.services.email import send_email
from src.services.upload_file_service import UploadFileService
from src.services.user import UserService

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def me(
    request: Request,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user(token)


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str, user_service: UserService = Depends(get_user_service)
):
    email = get_email_from_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_email(str(body.email))

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    avatar_url = UploadFileService(
        settings.CLOUDINARI_NAME,
        settings.CLOUDINARI_API_KEY,
        settings.CLOUDINARI_API_SECRET,
    ).upload_file(file, user.username)

    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
