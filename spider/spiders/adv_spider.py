"""Advertisement spider."""

import logging
import time
from typing import Any, Generator, Iterable

from itemloaders import ItemLoader
from scrapy import Request, Spider
from scrapy.http import Response

from settings import Settings
from spider.items import SpiderItem
from spider.project_utilities.save_utilities import save_adv_data, url_redis_storage

logger = logging.getLogger(__name__)


class AdvSpider(Spider):
    """Spider class."""

    name = 'adv_spider'

    def start_requests(self) -> Iterable[Request]:
        """Start requests functionality."""
        urls = url_redis_storage.get_urls()
        index = 0
        for url in urls:  # noqa
            time.sleep(Settings.SCRAP_TIMEOUT)
            index += 1
            yield Request(url=url, callback=self.parse)
            if Settings.DEBUG and index > 10:
                break
        url_redis_storage.delete_data('urls')

    def parse(self, response: Response, **kwargs: Any) -> Generator[dict, None, None]:
        """Parse response."""
        spider_item = ItemLoader(
            item=SpiderItem(),
            response=response,
            selector=response,
        )
        spider_item.add_value('url', response.url)
        spider_item.add_xpath('name', './/h1[@class="head"]/text()')
        spider_item.add_xpath('price', './/div[@class="price_value"]/strong/text()')
        spider_item.add_xpath('model', './/h1[@class="head"]/text()')
        spider_item.add_xpath(
            'region',
            ''.join(
                (
                    './/section[@id="userInfoBlock"]/ul[@class="checked-list ',
                    'unstyle mb-15"]/li[@class="item"]/div[@class',
                    '="item_inner"]/text()',
                ),
            ),
        )
        spider_item.add_xpath(
            'run',
            './/dd[@class="mhide"]/span[@class="argument"]/text()',
        )
        spider_item.add_xpath(
            'color',
            './/span[@class="car-color"]/following-sibling::text()',
        )
        spider_item.add_xpath(
            'salon',
            './/div[@class="technical-info"]/dl[@class="unstyle"]/dd/text()',
        )
        spider_item.add_xpath('seller', './/div[@class="seller_info_name bold"]/text()')
        spider_item.add_xpath(
            'adv_date',
            './/div[@class="size13 mt-5 mb-10 update-date"]/span/text()',
        )
        spider_item.load_item()
        logger.info(save_adv_data(spider_item.item.__dict__['_values']))
        yield spider_item.item.__dict__['_values']
