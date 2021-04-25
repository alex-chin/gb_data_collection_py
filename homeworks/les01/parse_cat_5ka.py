import json
import time
from pathlib import Path
import requests
import homeworks.les01.parse_5ka as p5ka

"""
https://5ka.ru/special_offers/

Задача организовать сбор данных, 
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные 
сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары 
исключительно соответсвующие данной категории.

пример структуры данных для файла: 
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""


class ParseCat5ka(p5ka.Parse5ka):
    def run(self):
        # список каталогов
        response = self._get_response(self.star_url, headers=self.headers)
        parent_cats = response.json()
        for parcat in parent_cats:
            # категории в каталоге
            url = self.star_url + parcat['parent_group_code']
            response = self._get_response(url, headers=self.headers)
            categories = response.json()
            for cat in categories:
                self.params['categories']=cat['group_code']
                for group in self._parse('https://5ka.ru/api/v2/special_offers/'):
                    print(group)

    def _parse(self, url: str):
        while url:
            urln = ''
            urln = self._clear_url(url)
            time.sleep(0.1)
            response = self._get_response(urln, headers=self.headers, params=self.params)
            print(self.params)
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product


if __name__ == "__main__":
    save_path = p5ka.get_save_path("products")
    url = "https://5ka.ru/api/v2/categories/"
    parser = ParseCat5ka(url, save_path)
    parser.run()
