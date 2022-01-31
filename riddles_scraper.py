from pprint import pprint

import scrapy
import re
import traceback
import time


class Riddles_Scraper(scrapy.Spider):
	name = "riddles_scraper"

	status = {}

	def start_requests(self):
		main_url = 'https://www.riddles.com'

		pages = [
			'/best-riddles',
			'/brain-teasers',
			'/classic-riddles',
			'/difficult-riddles',
			'/easy-riddles',
			'/funny-riddles',
			'/good-riddles',
			'/jokes-and-riddles',
			'/kids-riddles',
			'/logic-puzzles',
			'/math-riddles',
			'/medium-riddles',
			'/riddles-for-adults',
			'/short-riddles',
			'/video-riddles',
			'/what-am-i-riddles',
			'/what-is-it-riddles',
			'/who-am-i-riddles',
			'/who-is-it-riddles'
		]

		for page in pages:
			url = main_url + page
			yield scrapy.Request(url=url, callback=self.parse, meta={"category": page[1:]})

		# url = main_url + pages[-1]
		# yield scrapy.Request(url=url, callback=self.parse, meta={"category": pages[-1][1:]})



	def parse(self, response):
		print(f"Parsing : {response.url}")
		# input("Press enter...")

		counter = 0

		for idx, item in enumerate( response.css('div.panel.panel-default')):
			# Checking if div has riddle
			check_val = item.css('h3.panel-title.lead.inline::text')
			if len(check_val) == 0:
				print("="*50)
				print(f"No title found, idx : {idx}")
				# input(f"Press enter to continue...")
				continue

			title = item.css('h3.panel-title.lead.inline::text')[0].get()
			url_for_answer = item.css('div.panel-body.lead')[0].css('a.btn.btn-riddle.btn-lg.lead.hidden-print::attr(href)').get()
			if 'http' not in url_for_answer:
				url_for_answer = response.url + url_for_answer
				riddle_no = re.findall('\d+', url_for_answer.split("#")[-1])[0]
				# url_for_answer = url_for_answer.split("#")[0] + "/" + riddle_no
				url_for_answer = 'https://www.riddles.com' + "/" + riddle_no
				

			data =  {
						"category": response.meta['category'],
						"title": title,
						"m_url":url_for_answer
					}

			pprint(data)

			print("/"*50)
			print(f"Calling secondary scrape : {url_for_answer}, data['m_url'] : {data['m_url']}")
			print("/"*50)
			counter += 1

			yield scrapy.Request(url_for_answer, callback=self.parse_second, meta=data)

		if response.meta['category'] not in self.status:
			self.status[response.meta['category']] = counter
		else:
			self.status[response.meta['category']] += counter

		print(f"Total scraped in this page : {counter}")
		print(f"Url is : {response.url}")
		# print(f"In {response.meta['category']} : {self.status[response.meta['category']]}")
		pprint(self.status)
		# input("Press enter to continue...")
		# Going to next page
		next_page = response.css('ul.pagination').css('li')[-1].css('a::attr(href)').get()
		if next_page is not None:
			yield scrapy.Request(next_page, callback=self.parse, meta=response.meta)
		if next_page is None:
			pprint(self.status)
			print(f"Category : {response.meta['category']}")
			input("Press enter to continue...")


	def parse_second(self, response):

		title = response.meta['title']
		category = response.meta['category']

		sel = response.css('div.collapse.mar_top_15')[0]
		# Ref : https://doc.scrapy.org/en/latest/topics/selectors.html
		answer = response.css('div.collapse.mar_top_15')[0].xpath('div/div').get()
		answer = answer.replace('<div>\n\t\t\t\t\t\t\t<strong class="dark_purple">Answer</strong>: ', '').replace('\n\t\t\t\t\t\t</div>', '')
		answer = answer.replace('\xa0', '') # removing &nbsp character

		question = response.css('div.panel-body.lead')[0].xpath('div').get()
		question = question.replace('<div>\n\t\t\t\t<strong class="orange_dk hidden-print">Riddle:</strong>', '').replace('\n\t\t\t</div>', '').strip()

		result = {
					"category" : category,
					"title": title,
					"question": question,
					"answer": answer
				}

		yield result

