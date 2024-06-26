"""Advertisement apps routers."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import (
    AdvInList,
    AdvNameModelQuerySchema,
    AdvOut,
    AdvPeriodQuerySchema,
    AdvStatOutSchema,
    CreateAdvIn,
    UrlSchema,
)
from apps.common.base_routers import BaseRouterInitializer
from apps.common.dependencies import get_async_session
from apps.common.enum import JSENDStatus
from apps.common.schemas import JSENDFailOutSchema, JSENDOutSchema
from apps.common.user_dependencies import get_current_admin_user, get_current_user
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
    tags=['Advertisements application'],
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


@adv_router.get(
    '/list/advertisement/stat/',
    name='adv_stat',
    response_model=JSENDOutSchema[AdvStatOutSchema],
    summary='Get statistic information of given model.',
    responses={
        200: {'description': 'Successfully get advertisement stat info'},
        422: {'model': JSENDFailOutSchema, 'description': 'ValidationError'},
    },
    tags=['Advertisements application'],
)
async def get_advertisement_stat(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    car_info: Annotated[AdvNameModelQuerySchema, Depends()],
) -> dict:
    """Get advertisements stat info concerning max/min price and number/period."""
    return {
        'data': await adv_handlers.get_name_model_stat(request, session, car_info),
        'message': ''.join(
            (
                'Get stat info for advertisement with car ',
                'name: {name} and model: {model}'.format(
                    name=car_info.name,
                    model=car_info.model,
                ),
            ),
        ),
    }


@adv_router.post(
    '/admin/list/advertisement/',
    name='bulk_create',
    response_model=JSENDOutSchema,
    summary='Create many advertisement.',
    responses={
        200: {'description': 'Successfully created many advertisement.'},
        422: {'model': JSENDFailOutSchema, 'description': 'ValidationError'},
    },
    tags=['Admin advertisements application'],
)
async def bulk_create_adv(
    request: Request,
    user: Annotated[User, Depends(get_current_admin_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    advs: Annotated[AdvInList, Depends()],
) -> dict:
    """Create many advertisements."""
    await adv_handlers.bulk_create_adv(request, session, advs)
    return {
        'data': None,
        'message': 'Successfully created advertisements.',
    }


@adv_router.get(
    '/advertisement/{url}/',
    name='get_adv_by_url',
    response_model=JSENDOutSchema[AdvOut],
    summary='Get advertisement by url.',
    responses={
        200: {'description': 'Successfully created many advertisement.'},
        422: {'model': JSENDFailOutSchema, 'description': 'ValidationError'},
    },
    tags=['Advertisements application'],
)
async def get_adv_by_url(
    request: Request,
    url: Annotated[UrlSchema, Depends()],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> dict:
    """Get advertisement by its url."""
    advertisement = await adv_handlers.get_adv_by_url(request, session, url)
    if advertisement:
        return {
            'data': advertisement,
            'message': 'Successfully get advertisement by url path: {url}'.format(
                url=url,
            ),
        }
    return {
        'data': advertisement,
        'message': 'Nothing was found with url path: {url}'.format(url=url),
        'status': JSENDStatus.FAIL,
        'code': status.HTTP_404_NOT_FOUND,
    }
