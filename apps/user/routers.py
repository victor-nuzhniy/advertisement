"""User apps routers."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from apps.common.base_routers import BaseRouterInitializer
from apps.common.dependencies import get_async_session
from apps.common.schemas import JSENDFailOutSchema, JSENDOutSchema
from apps.user.handlers import user_handlers
from apps.user.models import User
from apps.user.schemas import (
    AdminPartiallyUserIn,
    AdminUserIn,
    AdminUserOut,
    CreateAdminUserIn,
    CreateUserIn,
    CreateUserOut,
)

users_router = APIRouter()

admin_user_router_initializer = BaseRouterInitializer(  # type: ignore
    router=users_router,
    in_schemas=(CreateAdminUserIn, AdminUserIn, AdminPartiallyUserIn),
    out_schema=AdminUserOut,
    model=User,
)

admin_user_router_initializer.initialize_routers()


@users_router.post(
    '/user/',
    name='create_user',
    response_model=JSENDOutSchema[CreateUserOut],
    summary='Create user',
    responses={
        200: {'description': 'Successful create user response'},
        422: {'model': JSENDFailOutSchema, 'description': 'ValidationError'},
    },
    tags=['Users application'],
)
async def create_user(
    request: Request,
    user: CreateUserIn,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> dict:
    """**Create user record**.

    **Input**:
    - **username**: user name, max 50 symbols, required
    - **email**: user email, only letters (a-z), numbers (0-9) and periods (.) are
    allowed, required
    - **password**: password, cannot be empty, required
    - **password_re_check**: password recheck, required

    **Return**:
    - **user_id**: int, id of created user
    - **login**: str, username of created user
    - **last_visit**: datetime, date and time of last successful user login
    - **email**: str, user email
    - **is_active**: bool, flag which indicates is user active
    - **role_id**: int, id of user role
    """
    created_user = await user_handlers.create_user(
        request=request,
        user=user,
        session=session,
    )
    return {
        'data': created_user,
        'message': 'Created user with id {id}'.format(id=created_user.id),
    }
