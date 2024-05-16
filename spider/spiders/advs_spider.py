"""Advertisements spider."""

import logging
import time
from typing import Any

from itemloaders import ItemLoader
from scrapy import Spider
from scrapy.http import Response

from settings import Settings
from spider.items import AdvSpiderItem
from spider.project_utilities.save_utilities import url_redis_storage

logger = logging.getLogger(__name__)


class AdvsSpider(Spider):
    """
    Spider class.

    Save advertisements links to redis storage.
    """

    name = 'advs_spider'
    allowed_domains = ['auto.ria.com']
    start_urls = ['https://auto.ria.com/uk/car/used/']
    page = 1

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """Parse response."""
        time.sleep(Settings.SCRAP_TIMEOUT)
        spider_item = ItemLoader(item=AdvSpiderItem(), selector=response)
        spider_item.add_xpath('urls', './/a[@class="address"]/@href')
        spider_item.load_item()
        url_redis_storage.add_urls(spider_item.item.get('urls', []))
        logger.info('Saved links from page {page}'.format(page=self.page))
        self.page += 1
        next_url = '{url}?page={page}'.format(url=self.start_urls[0], page=self.page)
        next_url = response.xpath(
            '//a[contains(@href, "{url}")]/@href'.format(url=next_url),
        ).get()
        if Settings.DEBUG and self.page < 3:
            return None
        if next_url:
            return response.follow(next_url)
