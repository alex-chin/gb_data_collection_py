import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from .instagram.spiders.instagram import InstagramSpider

# Задача 7

# Источник instgram
# Задача авторизованным пользователем обойти список произвольных тегов,
# Сохранить структуру Item олицетворяющую сам Tag (только информация о теге)
# Сохранить структуру данных поста, Включая обход пагинации. (каждый пост как отдельный item, словарь внутри node)
# Все структуры должны иметь след вид
# date_parse (datetime) время когда произошло создание структуры
# data - данные полученые от инстаграм
# Скачать изображения всех постов и сохранить на диск

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("instagram.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    tags = ["python"]
    crawler_process.crawl(
        InstagramSpider,
        login=os.getenv("INST_LOGIN"),
        password=os.getenv("INST_PSWORD"),
        tags=tags,
    )
    crawler_process.start()
