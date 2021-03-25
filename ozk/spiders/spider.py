import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import OzkItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class OzkSpider(scrapy.Spider):
	name = 'ozk'
	start_urls = ['https://blog.ozk.com/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="list-item-read-more btn-b"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		try:
			date = response.xpath('//span[@class="post-content-date post-content-date-post"]/text()').get().replace('in','').strip()
		except AttributeError:
			date = " "
		title = response.xpath('//h1/text()').get()
		if not title:
			title = response.xpath('//span[@class="hero-blog-label"]/text()').get()
		content = response.xpath('//div[@class="post-content-body post-content-body-post"]//text()').getall()
		if not content:
			content = response.xpath('//div[@class="entry-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=OzkItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
