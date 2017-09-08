# -*- coding: utf-8 -*-
import scrapy
from immo_crawler.items import ImmoCrawlerItem

class ListingsSpider(scrapy.Spider):
	name = 'leboncoin_buy'
	allowed_domains = ['leboncoin.fr']
	start_urls = ['https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/paris/?th=1&ret=1&ret=2']
	custom_settings = {
	'FEED_EXPORT_FIELDS': ["listingId", "url", "title", "date", "time", "price", "zip_code", "city", "propertyType", "rooms", "superficy", "description"],
	} 

	def parse(self, response):
		urls = response.xpath("//*[@id='listingAds']/section/section/ul/li/a/@href").extract()
		for url in urls:
			url = "https:" + str(url)
			yield scrapy.Request(url=url, callback=self.parse_details)
			#follow pagination link
		next_url = "https:" + str(response.xpath("//*[@id='next']/@href").extract_first())
		if next_url:
			yield scrapy.Request(url=next_url, callback=self.parse)

	def parse_details(self,response):
		items = ImmoCrawlerItem()
		items['listingId'] = response.xpath("//span[@class='flat-horizontal saveAd link-like']/@data-savead-id").extract_first()
		items['url'] = "https:" + response.xpath("//head/meta[@property='og:url']/@content").extract_first()
		items['title'] = response.xpath("//h1[@itemprop='name']/text()").extract_first().strip()
		items['date'] = response.xpath("//p[@itemprop='availabilityStarts']/@content").extract_first()
		items['time'] = response.xpath('//p[@itemprop="availabilityStarts"]/text()').re_first(r'\d\d:\d\d')
		price = response.xpath("//h2[span='Prix']/span[@class='value']/text()").extract_first()
		#sometimes, the price doest not exist on the listing and if the price doesn't exist then variable is None, but None not has method .strip() and the script has error in this case
		if price:
			items['price'] = price.strip()
		#this structure allows to take into account the cities that have two words
		items['zip_code'] = response.xpath("//h2/span[@itemprop='address']/text()").extract_first().strip().split()[-1]
		items['city'] = \
			' '.join(response.xpath("//h2/span[@itemprop='address']/text()").extract_first().strip().split()[:-1])
		items['propertyType'] = response.xpath("//h2[span='Type de bien']/span[@class='value']/text()").extract_first()
		items['rooms'] = response.xpath(u"//h2[span='Pièces']/span[@class='value']/text()").extract_first()
		items['superficy'] = response.xpath("//h2[span='Surface']/span[@class='value']/text()").extract_first()
		items['description'] = ' '.join(response.xpath("//div/p[@itemprop='description']/text()").extract())
		yield items


