import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    # если запись не найдена она создается
    def _get_or_create(self, session, model, filter_field, **data):
        instance = session.query(model).filter_by(**{filter_field: data[filter_field]}).first()
        if not instance:
            instance = model(**data)
        return instance

    def _add_comments(self, session, data):
        result = []
        # цикл по комментам 1 уровня
        for comment in data:
            author = self._get_or_create(
                session,
                models.Author,
                "id",
                name=comment["comment"]["user"]["full_name"],
                url=comment["comment"]["user"]["url"],
                id=comment["comment"]["user"]["id"],
            )
            comment_db = self._get_or_create(
                session, models.Comment, "id", **comment["comment"], author=author,
            )
            result.append(comment_db)
            # рекурсия по вложенным комментарием
            # комментарии конечны
            result.extend(self._add_comments(session, comment["comment"]["children"]))
        return result

    # основной метод работы с БД сканирование сайта и добавление постов
    def add_post(self, data):
        session = self.maker()
        # это но новый пост но для страховки
        # **data["post_data"] - раскрытие списка по параметрам
        post = self._get_or_create(session, models.Post, "id", **data["post_data"])
        # автор может быть уже есть, поэтому проверяем надо ли его создавать
        author = self._get_or_create(session, models.Author, "id", **data["author_data"])
        #  для каждого элемента в списке выполнить добавление
        tags = map(
            lambda tag_data: self._get_or_create(session, models.Tag, "name", **tag_data),
            data["tags_data"],
        )
        # подключили автора
        post.author = author
        # дополнили список тегов
        post.tags.extend(tags)
        # дополнили список комментариев
        post.comments.extend(self._add_comments(session, data["comments_data"]))
        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            session.rollback()
        finally:
            session.close()
