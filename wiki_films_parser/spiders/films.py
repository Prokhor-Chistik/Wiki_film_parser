import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]

    def start_requests(self):
        URL = "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        yield scrapy.Request(url=URL, callback=self.abc_films_parse)

    def abc_films_parse(self, response):
        blocks = response.css('#mw-pages > div > div')
        for block in blocks:
            for film_ in block.css('li'):
                film_url = 'https://ru.wikipedia.org' + film_.css('a').attrib['href']
                yield response.follow(film_url, callback=self.film_page_parse)

        next_page_url = None

        for urls in response.css('div#mw-pages > a'):
            if urls.css('::text').extract_first() == 'Следующая страница':
                next_page_url = 'https://ru.wikipedia.org' + urls.css('::attr(href)').extract_first()
                break

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.abc_films_parse)

    def film_page_parse(self, response):
        for i in response.css('tbody > tr'):
            if i.css('th ::text').get() == 'Режиссёр':
                yield {
                    'title': response.css('span.mw-page-title-main ::text').get(),
                    'director': i.css('td > span ::text').get()
                }

