"""Advertisement apps schemas."""

from datetime import date, datetime

from pydantic import Field, computed_field, field_validator
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
            examples=['2024-10-15'],
            description='Advertisement date creation in str',
        ),
    ]

    @computed_field
    def adv_date(self) -> date | None:
        """Create date from str."""
        try:
            date_object = datetime.strptime(self.created, '%Y-%m-%d').date()
        except ValueError:
            date_object = None
        return date_object


class AdvInList(BaseInSchema):
    """Advertisement schema list."""

    item_list: list[CreateAdvIn]


class AdvOut(BaseOutSchema):
    """Advertisement out schema."""

    id: int
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


class AdvPeriodQuerySchema(BaseInSchema):
    """Schema for period query string."""

    begin: Annotated[
        str | None,
        Field(examples=['2023-10-12'], description='Start period date.'),
    ] = None
    end: Annotated[
        str | None,
        Field(examples=['2023-11-12'], description='End period date.'),
    ] = None

    @field_validator('begin', 'end')
    @classmethod
    def validate_data(cls, date_value: str | None) -> date | None:
        """Validate and parse date_value."""
        if date_value is None:
            return date_value
        return datetime.strptime(date_value, '%Y-%m-%d').date()


class AdvNameModelQuerySchema(BaseInSchema):
    """Schema for name and/or model statistic."""

    name: Annotated[
        str | None,
        Field(max_length=100, examples=['Honda'], description='Car name.'),
    ]
    model: Annotated[
        str | None,
        Field(max_length=100, examples=['CR-V'], description='Car model.'),
    ]


class AdvStatOutSchema(BaseOutSchema):
    """Schema for statistical info concerning min/max price and number/period."""

    min_price: int
    max_price: int
    num_day: int
    num_week: int
    num_month: int
