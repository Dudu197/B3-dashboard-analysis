import scrapy

class IfixSpider(scrapy.Spider):
  name = "brickset_spider"
  def __init__(self, **kwargs):
    self.start_urls = ['https://statusinvest.com.br/indices/ifix']
    self.custom_settings = {
      # 'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, # Used for pipeline 1
      'FEED_FORMAT':'json',                                 # Used for pipeline 2
      'FEED_URI': 'ifix.json'                        # Used for pipeline 2
    }
    super().__init__(**kwargs)  # python3


  def parse(self, response):
    for items in response.css('[aria-label="Grid com a composição do IFIX"] .main-list'):
      for item in items.css('.item'):

        COMPANY_SELECTOR = '.company .w-100 ::text'
        TICKET_SELECTOR = '.company .ticker ::text'
        SECTOR_SELECTOR = '[title="Setor da empresa"] ::text'
        yield {
            'company': item.css(COMPANY_SELECTOR).extract_first(),
            'ticket': item.css(TICKET_SELECTOR).extract_first(),
            'sector': item.css(SECTOR_SELECTOR).extract_first(),
        }