"""Spider items module.

Define here the models for your scraped items

See documentation in:
https://docs.scrapy.org/en/latest/topics/items.html
"""

from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Field, Item


class AdditionalFunctionality:
    """Additional functionality for fields processing."""

    def get_name(self, name_data: str) -> str:
        """Get name from given data."""
        return name_data.split()[0]

    def get_model(self, model_data: str) -> str:
        """Get model from given data."""
        data_list = model_data.split()
        model = ''
        if len(data_list) > 1:
            model = data_list[1]
        return model

    def convert_str_num(self, price: str) -> int:
        """Convert price string to int."""
        cleaned_price = ''.join(filter(lambda el: el.isdigit(), price))
        if cleaned_price:
            return int(cleaned_price)
        return 0

    def convert_date(self, date_data: str) -> str:
        """Convert date data for format %d-%m-%Y."""
        month_dict = {
            'січ': 1,
            'лют': 2,
            'бер': 3,
            'кві': 4,
            'тра': 5,
            'чер': 6,
            'лип': 7,
            'сер': 8,
            'вер': 9,
            'жов': 10,
            'лис': 11,
            'гру': 12,
        }
        date_list = date_data.split()
        if len(date_list) == 4 and len(date_list[2]) > 2:
            month: int = month_dict.get(date_list[2][:3], 1)
            return '{year}-{month:02d}-{day}'.format(
                year=date_list[3],
                month=month,
                day=date_list[1],
            )
        return '2010-01-01'

    def check_none(self, data_value: str | None) -> str:
        """Check whether input is none and if it is, convert to empty str."""
        if data_value is None:
            return ''
        return data_value


add_func = AdditionalFunctionality()


class SpiderItem(Item):
    """Define the fields for your item here like: name = scrapy.Field()."""

    url = Field(
        output_processor=TakeFirst(),
    )
    name = Field(
        input_processor=MapCompose(add_func.check_none, str.strip, add_func.get_name),
        output_processor=TakeFirst(),
    )
    price = Field(
        input_processor=MapCompose(add_func.check_none, add_func.convert_str_num),
        output_processor=TakeFirst(),
    )
    model = Field(
        input_processor=MapCompose(add_func.check_none, str.strip, add_func.get_model),
        output_processor=TakeFirst(),
    )
    region = Field(
        input_processor=MapCompose(add_func.check_none, str.strip),
        output_processor=TakeFirst(),
    )
    run = Field(
        input_processor=MapCompose(add_func.check_none, add_func.convert_str_num),
        output_processor=TakeFirst(),
    )
    color = Field(
        input_processor=MapCompose(add_func.check_none, str.strip),
        output_processor=TakeFirst(),
    )
    salon = Field(
        input_processor=MapCompose(add_func.check_none, str.strip),
        output_processor=TakeFirst(),
    )
    seller = Field(
        input_processor=MapCompose(add_func.check_none, str.strip),
        output_processor=TakeFirst(),
    )
    created = Field(
        input_processor=MapCompose(
            add_func.check_none,
            str.strip,
            add_func.convert_date,
        ),
        output_processor=TakeFirst(),
    )


class AdvSpiderItem(Item):
    """Define urls to scrap data."""

    urls = Field()
