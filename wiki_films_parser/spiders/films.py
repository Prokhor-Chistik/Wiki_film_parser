import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]

    def start_requests(self):
        URL = "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        #URL = "https://ru.wikipedia.org/wiki/%3F_(%D1%84%D0%B8%D0%BB%D1%8C%D0%BC)"
        #URL = "https://ru.wikipedia.org/wiki/8_%D0%BF%D0%BE%D0%B4%D1%80%D1%83%D0%B3_%D0%9E%D1%83%D1%88%D0%B5%D0%BD%D0%B0"
        yield scrapy.Request(url=URL, callback=self.abc_films_parse)

    film_genre = ''
    film_director = ''
    film_country = ''
    film_year = ''

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

        film_genre = ''
        film_director = ''
        film_country = ''
        film_year = ''

        for i in response.css('tbody > tr'):

            if 'Жанр' in str(i.css('th ::text').get()):
                for j in i.css('td a'):
                    if (j.css('::text').get() is not None) and (not any(c.isdigit() for c in str(j.css('::text').get()))):
                        if film_genre == '':
                            film_genre += j.css('::text').get()
                        else:
                            film_genre += ',' + j.css('::text').get()

            elif (i.css('th ::text').get()) == 'Режиссёр':
                film_director = i.css('td :last-child ::text').get()
            elif (i.css('th ::text').get()) == 'Страна':
                film_country = i.css('td a ::text').get()
            elif (i.css('th ::text').get()) == 'Год':
                film_year = i.css('td a:last-child ::text').get()
        yield {
            'title': response.css('tbody > tr:nth-child(1) > th ::text').get(),
            'genre': film_genre,
            'director': film_director,
            'country': film_country,
            'year': film_year
        }











