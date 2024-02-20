import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org", "www.imdb.com"]

    def start_requests(self):
        URL = "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        #URL = "https://ru.wikipedia.org/wiki/Вторжение_далеков_на_Землю"
        #URL = "https://ru.wikipedia.org/wiki/Вторжение_далеков_на_Землю_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/Глаз_3:_Бесконечность"
        #URL = "https://ru.wikipedia.org/wiki/Вальс_«Голубой_Дунай»_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/Миссис_Паркер_и_порочный_круг"
        #URL = "https://ru.wikipedia.org/wiki/Безмолвный_свет"
        #URL = "https://ru.wikipedia.org/wiki/Доктор_Кто_(фильм, _1996)"
        #URL = "https://ru.wikipedia.org/wiki/Идентификация_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/Наше_будущее_(фильм)"
        #URL = "https://ru.wikipedia.org/wiki/42_(фильм)"

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
        """
        Функция парсинга страницы фильма с выуживанием информации по:
        названию фильма; его жанру, информации о режиссере, стране производства и года выпуска.
        """

        film_title = ''
        film_genre = ''
        film_director = ''
        film_country = ''
        film_year = ''
        film_IMDb_url = ''

        director_count = 0
        genre_count = 0

        countries = {
            'СССР': 'СССР', 'Росси': 'Россия', 'США': 'США', 'Поль': 'Польша', 'ФРГ': 'ФРГ',
            'Нидерлан': 'Нидерланды', 'Испан': 'Испания', 'Великобрита': 'Великобритания',
            'Таилан': 'Таиланд', 'Гонкон': 'Гонконг', 'Республики Корея': 'Республика Корея',
            'Итал': 'Италия', 'британ': 'Великобритания', 'америка': 'США'
        }
        genres = {
            'фантаст': 'фантастика', ' комеди': 'комедия', 'мелодрама':'мелодрама', ' драма': ' драма',
            'ужас': 'фильм ужасов','триллер': 'триллер', 'окументальны': 'Документальный фильм',
            'боевик': 'боевик', 'фэнтези': 'фэнтези', 'приключе': 'приключения', 'историческ': 'исторический фильм',
            'кранизация': 'экранизация романа', 'криминальны': 'криминальный фильм', 'биографическ': 'биографический фильм',
            'военн': 'военный фильм', 'трагикомеди': 'трагикомедия', 'детектив': 'детектив', 'вестерн': 'вестерн',
            'сказка': 'сказка'
        }

        # итерирование таблиц страницы фильма по их строкам.
        for i in response.css('tbody > tr'):

            # проверка левых ячеек строки (первый столбец) на предмет наличия в них ключевых слов:
            # ":Жанр", "Режиссёр", "Стран", "Год", "Дата выхода", "Первый показ",
            # с целью определения строчного индекса для извлечения соответсвующей целевой информации.

            #============================================== Жанр =================================================================

            # определение в таблице строчного индекса соответсвующего ключевому слову "Жанр".
            if 'Жанр' in str(i.css('th ::text').get()) and (genre_count == 0):
                # счетчик для учета данных строки с совпадением по ключевому слову "Жанр"
                # только лишь для первого совпадения (первой таблицы).
                genre_count = 1
                # при совпадении ключевого слова итерирование правой ячейки с целевой информацией
                # на наличие подстрок с селектором "a".
                for j in i.css('td a'):
                    # селекция текстовой информации из подстрок с селектором "a" на предмет допустимых данных.
                    if (
                        (str(j.css('::text').get()) is not None) and
                        (str(j.css('::text').get()) not in film_genre) and
                        ('[' not in str(j.css('::text').get())) and
                        ('(' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != ', ')
                    ):
                        # последовательная запись (через запятую) в целевую переменную отселектированных данных.
                        if film_genre == '':
                            film_genre += str(j.css('::text').get())
                        else:
                            film_genre += ', ' + str(j.css('::text').get())

                # при совпадении ключевого слова итерирование правой ячейки с целевой информацией
                # на наличие подстрок с селектором "span".
                for j in i.css('td span'):
                    # селекция текстовой информации из подстрок с селектором "span" на предмет допустимых данных.
                    if (
                        (str(j.css('::text').get()) is not None) and
                        (str(j.css('::text').get()) not in film_genre) and
                        ('[' not in str(j.css('::text').get())) and
                        ('(' not in str(j.css('::text').get())) and
                        (str(j.css('::text').get()) != '\n') and
                        (str(j.css('::text').get()) != ', ')
                    ):
                        # последовательная запись (через запятую) в целевую переменную отселектированных данных.
                        if film_genre == '':
                            film_genre += str(j.css('::text').get())
                        else:
                            film_genre += ', ' + str(j.css('::text').get())

                # замена в целевой переменной символа неразрывного пробела на пробел обычный.
                film_genre = film_genre.replace('\u00A0', ' ')
                # замена в целевой переменной символа переноса строки на пустую строку.
                film_genre = film_genre.replace('\n', '')

            # ========================================= Режиссёр =================================================================

            # определение в таблице строчного индекса соответсвующего ключевому слову "Режиссёр".
            elif ('Режиссёр' in str(i.css('th ::text').get())) and (director_count == 0):
                # счетчик для учета данных строки с совпадением по ключевому слову "Режиссёр"
                # только лишь для первого совпадения (первой таблицы).
                director_count = 1
                # при совпадении ключевого слова итерирование правой ячейки с целевой информацией
                # на наличие подстрок с селектором "span".
                for j in i.css('td span'):
                    # селекция текстовой информации из подстрок с селектором "span" на предмет допустимых данных.
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
                        # последовательная запись (через запятую) в целевую переменную отселектированных данных.
                        if film_director == '':
                            film_director += str(j.css('::text').get())
                        else:
                            film_director += ', ' + str(j.css('::text').get())

                # при совпадении ключевого слова итерирование правой ячейки с целевой информацией
                # на наличие подстрок с селектором "a".
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

                # замена в целевой переменной недопустимых символов.
                film_director = film_director.replace('\u00A0', ' ')
                film_director = film_director.replace('\n', '')

            # ========================================= Страна =================================================================

            # определение в таблице строчного индекса соответсвующего ключевому слову "Страна".
            elif 'Стран' in str(i.css('th ::text').get()):
                # при совпадении ключевого слова итерирование правой ячейки с целевой информацией
                # на наличие подстрок с селектором "a".
                for j in i.css('td a'):
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

                # при совпадении ключевого слова итерирование правой ячейки с целевой информацией
                # на наличие подстрок с селектором "span".
                for j in i.css('td span'):
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

                # если название страны не было найдено, вытаскивание названия из картинки с флагом.
                if film_country == '':
                    for j in i.css('td a'):
                        for k in countries:
                            if k in str(j.css('::attr(title)').get()):
                                if film_country == '':
                                    film_country += countries[k]
                                else:
                                    film_country += ', ' + countries[k]


            # ========================================= Год выхода =================================================================

            # определение в таблице строчного индекса соответсвующего ключевым словам "Год", "Дата выхода", "Первый показ".
            elif (str(i.css('th ::text').get()) == 'Год') or (str(i.css('th ::text').get()) == 'Дата выхода') or (str(i.css('th ::text').get()) == 'Первый показ'):
                film_year = i.css('td a:last-child ::text').get()

                if (film_year is None) or ('[' in str(film_year)):
                    film_year = i.css('td a ::text').get()
                    if (film_year is None) or ('[' in str(film_year)):
                        film_year = i.css('td ::text').get()
                        film_year = str(film_year).replace('\n', '')

                if (film_year is None) or (film_year == ''):
                    film_year = i.css('td li ::text').get()

                if (film_year is None) or (film_year == ''):
                    film_year = i.css('td > span ::text').get()

                # if (film_year == 'None') or (film_year is None) or (film_year == ''):
                #     for j in i.css('td *'):
                #         if (str(j.css('::text').get()) not in film_year):
                #             film_year = str(j.css('::text').get())


            # =============================== Получение ссылки на адрес страницы фильма на сайте IMDb =================================================================

            # определение в таблице строчного индекса соответсвующего ключевому слову "IMDb"
            # и запись в переменную "film_IMDb_url" ссылки на адрес страницы фильма на сайте IMDb.
            elif (str(i.css('th a::text').get()) == 'IMDb'):
                film_IMDb_url = str(i.css('td span a::attr(href)').get())


        # ========================================= Название фильма =================================================================

        film_title = str(response.css('tbody > tr:nth-child(1) > th ::text').get())
        if (film_title == 'рус.') or ('\u00A0' in film_title) or ('\n' in film_title) or (film_title == 'Кровавый бордель') or ('/' in film_title):
            film_title = str(response.css('#firstHeading > span ::text').get())
            if '(фильм' in film_title:
                film_title = film_title[:(film_title.find('(')-1)]

        # ======================================= Дополнительный поиск в тексте основной страницы =================================================================

        # Если целевая информация из таблиц не получена, поиск её в основном тексте страницы.
        # Ищем информацию по жанру фильма.
        if film_genre == '':
            _temp = ''
            for i in response.css('#mw-content-text > div.mw-content-ltr.mw-parser-output > p:nth-child(2)').get():
                _temp += str(i)
            for k in genres:
                if (k in _temp) and (genres[k] not in film_genre):
                    if film_genre == '':
                        film_genre += genres[k]
                    else:
                        film_genre += ', ' + genres[k]

        # Ищем информацию по стране производства.
        if film_country == '':
            _temp = ''
            for i in response.css('#mw-content-text > div.mw-content-ltr.mw-parser-output > p:nth-child(2)').get():
                _temp += str(i)
            for k in countries:
                if (k in _temp) and (countries[k] not in film_country):
                     if film_country == '':
                        film_country += countries[k]
                     else:
                        film_country += ', ' + countries[k]

        #Ищем информацию по году выхода фильма.
        if (film_year is None) or (film_year == ''):
            _temp = ''
            for i in response.css('#mw-content-text > div.mw-content-ltr.mw-parser-output > p:nth-child(2)').get():
                _temp += str(i)
            if ' год' in _temp:
                _index = _temp.find(' год')
                film_year = _temp[_index-4: _index:]


        # Запись полученных на странице фильма (сайта Википедия) данных в словарь.
        item = {
            'title': film_title,
            'genre': film_genre,
            'director': film_director,
            'country': film_country,
            'year': film_year
        }

        yield response.follow(url=film_IMDb_url, callback=self.IMDb_film_page_parse, cb_kwargs={'item': item})

    def IMDb_film_page_parse(self, response, item):
        film_IMDb_rating =''
        film_IMDb_rating = response.css('#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-304f99f6-0.fSJiHR > section > div:nth-child(4) > section > section > div.sc-491663c0-3.bdjVSf > div.sc-3a4309f8-0.bjXIAP.sc-69e49b85-1.llNLpA > div > div:nth-child(1) > a > span > div > div.sc-bde20123-0.dLwiNw > div.sc-bde20123-2.cdQqzc > span ::text').get()
        item['IMDb rating'] = film_IMDb_rating

        # Запись полученной целевой информации о фильме в итоговый словарь через генератор
        yield item











