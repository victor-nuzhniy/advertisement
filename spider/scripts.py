"""Script for running spiders."""

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from spider.spiders.adv_spider import AdvSpider
from spider.spiders.advs_spider import AdvsSpider

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

from twisted.internet import defer, reactor


def run_crawler() -> None:
    """Run spiders sequentially."""
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    @defer.inlineCallbacks
    def crawl():  # type: ignore
        yield runner.crawl(AdvsSpider)
        yield runner.crawl(AdvSpider)
        reactor.stop()  # type: ignore

    crawl()
    reactor.run()  # type: ignore
