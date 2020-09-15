import scrapy

class IndicatorsSpider(scrapy.Spider):
  name = "brickset_spider"
  def __init__(self, ticket='', **kwargs):
    self.start_urls = [f'https://statusinvest.com.br/acoes/{ticket}']
    self.custom_settings = {
      # 'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, # Used for pipeline 1
      'FEED_FORMAT':'json',                                 # Used for pipeline 2
      'FEED_URI': f'crawlers/{ticket}.json'                        # Used for pipeline 2
    }
    super().__init__(**kwargs)  # python3


  def parse(self, response):
    for items in response.css('.indicators'):
      for item in items.css('.item'):

        TITLE_SELECTOR = '.title ::text'
        VALUE_SELECTOR = '.value ::text'
        yield {
            'title': item.css(TITLE_SELECTOR).extract_first(),
            'value': item.css(VALUE_SELECTOR).extract_first(),
        }