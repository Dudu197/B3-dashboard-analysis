import scrapy

class IndicatorsSpider(scrapy.Spider):
  name = "brickset_spider"
  def __init__(self, ticket='', **kwargs):
    self.start_urls = [f'https://statusinvest.com.br/fundos-imobiliarios/{ticket}']
    self.custom_settings = {
      # 'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, # Used for pipeline 1
      'FEED_FORMAT':'json',                                 # Used for pipeline 2
      'FEED_URI': f'crawlers/{ticket}.json'                        # Used for pipeline 2
    }
    super().__init__(**kwargs)  # python3


  def parse(self, response):
    for items in response.css('.top-info.top-info-2.top-info-md-3.top-info-lg-n'):
      for item in items.css('.info'):

        TITLE_SELECTOR = '.title.m-0 ::text'
        VALUE_SELECTOR = '.value ::text'
        yield {
            'title': item.css(TITLE_SELECTOR).extract_first(),
            'value': item.css(VALUE_SELECTOR).extract_first(),
        }