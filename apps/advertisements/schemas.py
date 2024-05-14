"""Advertisement apps schemas."""

from datetime import date, datetime

from pydantic import Field, computed_field
from typing_extensions import Annotated

from apps.common.schemas import BaseInSchema, BaseOutSchema


class CreateAdvIn(BaseInSchema):
    """Advertisement creation in schema."""

    url: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            examples=['https://heelo.org'],
            description='Advertisements url',
        ),
    ]
    name: Annotated[
        str,
        Field(min_length=1, max_length=100, examples=['Mazda'], description='Car name'),
    ]
    price: Annotated[
        int,
        Field(description='Car price in usd', examples=[12000]),
    ]
    model: Annotated[
        str,
        Field(min_length=1, max_length=100, examples=['6'], description='Car model'),
    ]
    region: Annotated[
        str,
        Field(min_length=1, max_length=100, examples=['Dnipro'], description='Region'),
    ]
    run: Annotated[
        int,
        Field(description="Distance the car's run", examples=[30000]),
    ]
    color: Annotated[
        str,
        Field(max_length=100, examples=['red'], description='Car color'),
    ]
    salon: Annotated[
        str,
        Field(max_length=50, examples=['hatchback'], description='Car salon type'),
    ]
    seller: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            examples=['Irina 066 666-66-66'],
            description='Seller contacts',
        ),
    ]
    created: Annotated[
        str,
        Field(
            exclude=True,
            examples=['22-10-2024'],
            description='Advertisement date creation in str',
        ),
    ]

    @computed_field
    def adv_date(self) -> date | None:
        """Create date from str."""
        try:
            date_object = datetime.strptime(self.created, '%d-%m-%Y').date()
        except ValueError:
            date_object = None
        return date_object


class AdvOut(BaseOutSchema):
    """Advertisement out schema."""

    url: Annotated[
        str,
        Field(examples=['https://heelo.org'], description='Advertisements url'),
    ]
    name: Annotated[
        str,
        Field(examples=['Mazda'], description='Car name'),
    ]
    price: Annotated[
        int,
        Field(description='Car price in usd', examples=[12000]),
    ]
    model: Annotated[
        str,
        Field(examples=['6'], description='Car model'),
    ]
    region: Annotated[
        str,
        Field(examples=['Dnipro'], description='Region'),
    ]
    run: Annotated[
        int,
        Field(description="Distance the car's run", examples=[30000]),
    ]
    color: Annotated[
        str,
        Field(examples=['red'], description='Car color'),
    ]
    salon: Annotated[
        str,
        Field(examples=['hatchback'], description='Car salon type'),
    ]
    seller: Annotated[
        str,
        Field(examples=['Irina 066 666-66-66'], description='Seller contacts'),
    ]
    adv_date: Annotated[date, Field(description='Advertisement created at in date')]
    created_at: Annotated[datetime, Field(description='Field creation datetime')]
