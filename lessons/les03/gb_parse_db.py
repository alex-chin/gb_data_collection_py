import time
import typing

import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4

from dateutil import parser as date_parser


# Источник https://gb.ru/posts/
# Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:
# - url страницы материала
# - Заголовок материала
# - Первое изображение материала (Ссылка)
# - Дата публикации (в формате datetime)
# - имя автора материала
# - ссылка на страницу автора материала
# - комментарии в виде (автор комментария и текст комментария)
#
# Структуру сохраняем в MongoDB

# этот класс проводит
# 1 поиск ссылок пагинации на странице
# 2 поиск ссылок на посты
# 3 переход на отдельные страницы блога и получение конкретной информации

class GbBlogParse:

    def __init__(self, start_url, collection):
        # начальное значение для контроля временм
        self.time = time.time()
        self.start_url = start_url
        # структура БД куда пишем
        self.collection = collection
        # список пройденных ссылок
        self.done_urls = set()
        # список задач
        self.tasks = []
        # начальная задача для выполнения цикла
        self._init_task()

    def _init_task(self):
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

    # выполнение запроса по @url и получение ответа
    def _get_response(self, url, *args, **kwargs):
        # задержка каждую секунду на пол секунды
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    # получение структура для поиска конкретных элементов
    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    # построить задачу для отложенного вызова для постановки в очередь
    # @callback - передать функцию для обертки в задачу
    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        # обертка задачи
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        # если урл есть в множестве возврат нулевой функции
        if url in self.done_urls:
            return lambda *_, **__: None
        # учесть этот @url в множестве
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href")) for itm in tags_list if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": url,
                "id": soup.find("comments").attrs.get("commentable-id"),
                # ссылку берем из <div class="hidden" itemprop="image">
                "image": soup.find("div", attrs={"itemprop": "image", "class": "hidden"}).text,
                # дату берем из атрибута
                # <time class="text-md text-muted m-r-md" datetime="2021-03-30T15:08:21+03:00" itemprop="datePublished">
                #   30 марта 2021
                # </time>
                "datetime": self._get_date_iso(soup.find("time", {'class': 'text-md'})['datetime'])
            },
            "author_data": {
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
                "name": author_tag.text,
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id")),
        }
        return data

    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data = response.json()
        return data

    # преобразует строку формата ISO вида 2021-03-30T15:08:21+03:00 в объект datetime
    def _get_date_iso(self, date_str):
        # только с python 3.7
        # return dt.datetime.fromisoformat(date_str),
        return date_parser.parse(date_str)

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    collection = MongoClient()["gb_parse_08_05"]["gb_blog"]
    parser = GbBlogParse("https://gb.ru/posts", collection)
    parser.run()
