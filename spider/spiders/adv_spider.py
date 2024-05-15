"""Advertisement spider."""

from typing import Any, Generator, Iterable

from scrapy import Request, Spider
from scrapy.http import Response


class QuoteSpider(Spider):
    """Spider class."""

    name = 'adv_spider'

    def start_requests(self) -> Iterable[Request]:
        """Start requests functionality."""
        urls = [
            'https://auto.ria.com/uk/auto_honda_cr-v_36270838.html',
        ]
        for url in urls:  # noqa
            yield Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Generator[dict, None, None]:
        """Parse response."""
        name, model = self.get_name_and_model(
            response.xpath('.//h1[@class="head"]/text()').get(default='').strip(),
        )
        price = self.convert_str_num(
            response.xpath('.//div[@class="price_value"]/strong/text()').get(
                default='',
            ),
        )
        run = self.convert_str_num(
            response.xpath('.//dd[@class="mhide"]/span[@class="argument"]/text()')
            .get(default='')
            .strip(),
        )
        adv_date = self.convert_date(
            response.xpath(
                './/div[@class="size13 mt-5 mb-10 update-date"]/span/text()',
            ).get(),
        )
        yield {
            'url': response.url,
            'name': name,
            'price': price,
            'model': model,
            'region': response.xpath(
                ''.join(
                    (
                        './/section[@id="userInfoBlock"]/ul[@class="checked-list ',
                        'unstyle mb-15"]/li[@class="item"]/div[@class',
                        '="item_inner"]/text()',
                    ),
                ),
            )
            .get(default='')
            .strip(),
            'run': run,
            'color': response.xpath(
                './/span[@class="car-color"]/following-sibling::text()',
            )
            .get(default='')
            .strip(),
            'salon': response.xpath(
                './/div[@class="technical-info"]/dl[@class="unstyle"]/dd/text()',
            )
            .get(default='')
            .strip(),
            'seller': response.xpath('.//div[@class="seller_info_name bold"]/text()')
            .get(default='')
            .strip(),
            'adv_date': adv_date,
        }

    def get_name_and_model(self, name_data: str) -> tuple:
        """Get name and model from given data."""
        data_list = name_data.split()
        name, model = '', ''
        if len(data_list) > 1:
            name, model = data_list[0], data_list[1]
        else:
            name = data_list[0]
        return name, model

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
