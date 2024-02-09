import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]

    def start_requests(self):
        URL = "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        #URL = "https://ru.wikipedia.org/wiki/4_американских_композитора"
        #URL = "https://ru.wikipedia.org/wiki/300_спартанцев_(фильм,_2006)"
        #URL = "https://ru.wikipedia.org/wiki/32-е_августа_на_Земле"
        #URL = "https://ru.wikipedia.org/wiki/Байки_из_склепа:_Кровавый_бордель"
        #URL = "https://ru.wikipedia.org/wiki/Александр_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/Автомобильные_воры"
        #URL = "https://ru.wikipedia.org/wiki/79,_Парк-авеню"
        #URL = "https://ru.wikipedia.org/wiki/Красная_река_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/42-я_улица_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/Затерянные_в_космосе_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/44_минуты"
        #URL = "https://ru.wikipedia.org/wiki/Атомный_поезд"
        #URL = "https://ru.wikipedia.org/wiki/Доктор_Кто_(фильм, _1996)"

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

        film_title = ''
        film_genre = ''
        film_director = ''
        film_country = ''
        film_year = ''
        director_count = 0

        for i in response.css('tbody > tr'):

            if 'Жанр' in str(i.css('th ::text').get()):
                for j in i.css('td a'):
                    if (
                        (str(j.css('::text').get()) is not None) and
                        (str(j.css('::text').get()) not in film_genre) and
                        ('[' not in str(j.css('::text').get())) and
                        ('(' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != ', ')
                    ):
                        if film_genre == '':
                            film_genre += str(j.css('::text').get())
                        else:
                            film_genre += ', ' + str(j.css('::text').get())

                for j in i.css('td span'):
                    if (
                        (str(j.css('::text').get()) is not None) and
                        (str(j.css('::text').get()) not in film_genre) and
                        ('[' not in str(j.css('::text').get())) and
                        ('(' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != ', ')
                    ):
                        if film_genre == '':
                            film_genre += str(j.css('::text').get())
                        else:
                            film_genre += ', ' + str(j.css('::text').get())

                film_genre = film_genre.replace('\u00A0', ' ')

            elif ('Режиссёр' in str(i.css('th ::text').get())) and (director_count == 0):
                director_count = 1
                for j in i.css('td span'):
                    if (
                        (str(j.css('::text').get()) is not None) and
                        (str(j.css('::text').get()) not in film_director) and
                        ('[' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != '\u00A0') and
                        ('рус.' not in str(j.css('::text').get())) and
                        ('англ.' not in str(j.css('::text').get())) and
                        ('кит.' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\u00A0(') and
                        (str(j.css('::text').get()) != 'ru') and
                        (str(j.css('::text').get()) != 'en')
                    ):
                        if film_director == '':
                            film_director += str(j.css('::text').get())
                        else:
                            film_director += ', ' + str(j.css('::text').get())

                for j in i.css('td a'):
                    if (
                        (str(j.css('::text').get()) is not None) and
                        (str(j.css('::text').get()) not in film_director) and
                        ('[' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != '\u00A0') and
                        ('рус.' not in str(j.css('::text').get())) and
                        ('англ.' not in str(j.css('::text').get())) and
                        ('кит.' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\u00A0(') and
                        (str(j.css('::text').get()) != 'ru') and
                        (str(j.css('::text').get()) != 'en')
                    ):
                        if film_director == '':
                            film_director += str(j.css('::text').get())
                        else:
                            film_director += ', ' + str(j.css('::text').get())

                film_director = film_director.replace('\u00A0', ' ')

            elif 'Стран' in str(i.css('th ::text').get()):
                for j in i.css('td :last-child'):
                    if (
                        (j.css('::text').get() is not None) and
                        (str(j.css('::text').get()) not in film_country) and
                        ('[' not in str(j.css('::text').get())) and
                        ('(' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != '\u00A0') and
                        (str(j.css('::text').get()) != ' ')
                    ):
                        if film_country == '':
                            film_country += str(j.css('::text').get())
                        else:
                            film_country += ', ' + str(j.css('::text').get())

            elif (str(i.css('th ::text').get()) == 'Год') or (str(i.css('th ::text').get()) == 'Дата выхода') or (str(i.css('th ::text').get()) == 'Первый показ'):
                film_year = i.css('td a:last-child ::text').get()
                if (film_year is None) or ('[' in str(film_year)):
                    film_year = i.css('td a ::text').get()
                    if (film_year is None) or ('[' in str(film_year)):
                        film_year = str(i.css('td ::text').get())
                        film_year = film_year.replace('\n', '')


        film_title = str(response.css('tbody > tr:nth-child(1) > th ::text').get())
        if (film_title == 'рус.') or ('\u00A0' in film_title) or (film_title == 'Кровавый бордель'):
            film_title = str(response.css('#firstHeading > span ::text').get())

        yield {
            'title': film_title,
            'genre': film_genre,
            'director': film_director,
            'country': film_country,
            'year': film_year
        }











