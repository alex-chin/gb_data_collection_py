from pathlib import Path
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


# этот класс сначала считывает все категоии, а потом все продукты в категории
class ParseCat5ka(p5ka.Parse5ka):
    # @url_cat - ссылка получения списка категорий
    def __init__(self, url_cat, url_prod, save_path: Path):
        self.url_cat = url_cat
        super().__init__(url_prod, save_path)

    def run(self):
        # список каталогов
        response = self._get_response(self.url_cat, headers=self.headers)
        parent_cats = response.json()
        # перебор категорий
        for parent_cat in parent_cats:
            code_group = parent_cat['parent_group_code']
            name_group = parent_cat['parent_group_name']
            file_path = self.save_path.joinpath(f"{code_group}-{self._clear_name(name_group)}.json")
            print(parent_cat['parent_group_code'], name_group)
            # инициализация структуры
            cat_content = {"name": name_group, "code": code_group, "products": []}
            # параметр запроса @categories
            self.params['categories'] = code_group
            for product in self._parse(self.star_url):
                cat_content['products'].append(product)
            self._save(cat_content, file_path)

    # готовит содержимое строки для именования файла
    def _clear_name(self, name_file):
        clean_str = ''.join(e for e in name_file if e.isalnum())
        return clean_str[:10]


if __name__ == "__main__":
    save_path = p5ka.get_save_path("products")
    url_cat = "https://5ka.ru/api/v2/categories/"
    url_prod = "https://5ka.ru/api/v2/special_offers/"
    parser = ParseCat5ka(url_cat, url_prod, save_path)
    parser.run()
