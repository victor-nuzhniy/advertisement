"""Advertisement apps routers."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import AdvOut, AdvPeriodQuerySchema, CreateAdvIn
from apps.common.base_routers import BaseRouterInitializer
from apps.common.dependencies import get_async_session
from apps.common.schemas import JSENDFailOutSchema, JSENDOutSchema
from apps.common.user_dependencies import get_current_user
from apps.user.models import User

adv_router = APIRouter()

admin_adv_router_initializer = BaseRouterInitializer(  # type: ignore
    router=adv_router,
    in_schemas=(CreateAdvIn, CreateAdvIn, CreateAdvIn),
    out_schema=AdvOut,
    model=Advertisement,
)

admin_adv_router_initializer.initialize_routers()


@adv_router.get(
    '/list/advertisement/period/',
    name='adv_period',
    response_model=JSENDOutSchema[AdvOut],
    summary='Get advertisement list by given period.',
    responses={
        200: {'description': 'Successfully get advertisement list by period'},
        422: {'model': JSENDFailOutSchema, 'description': 'ValidationError'},
    },
    tags=['Advertisement application'],
)
async def get_advertisement_by_period(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    period: Annotated[AdvPeriodQuerySchema, Depends()],
) -> dict:
    """Get advertisement list by period."""
    return {
        'data': await adv_handlers.get_adv_period_list(request, session, period),
        'message': ''.join(
            (
                'Get advertisements list with begin - {begin}'.format(
                    begin=period.begin,
                ),
                ' and end - {end} period'.format(end=period.end),
            ),
        ),
    }
