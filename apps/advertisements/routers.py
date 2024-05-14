"""Advertisement apps routers."""

from fastapi import APIRouter

from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import AdvOut, CreateAdvIn
from apps.common.base_routers import BaseRouterInitializer

adv_router = APIRouter()

admin_adv_router_initializer = BaseRouterInitializer(  # type: ignore
    router=adv_router,
    in_schemas=(CreateAdvIn, CreateAdvIn, CreateAdvIn),
    out_schema=AdvOut,
    model=Advertisement,
)

admin_adv_router_initializer.initialize_routers()
