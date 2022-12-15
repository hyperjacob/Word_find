# компоненты библиотеки для описания структуры таблицы
from sqlalchemy import Column, Integer, Boolean, ForeignKey
# импортируем модуль для связки таблиц
from sqlalchemy.orm import relationship, backref

# импортируем модель пользователей для связки моделей
from models.users import Users
from data_base.dbcore import Base


class Boolset(Base):
    """
    Класс для создания таблицы "настройки",
    основан на декларативном стиле SQLAlchemy
    """
    # название таблицы
    __tablename__ = 'boolset'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    play = Column(Boolean)
    name = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))
    # для каскадного удаления данных из таблицы
    users = relationship(
        Users,
        backref=backref('boolset',
                        uselist=True,
                        cascade='delete,all'))
