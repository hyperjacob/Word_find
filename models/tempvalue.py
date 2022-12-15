# компоненты библиотеки для описания структуры таблицы
from sqlalchemy import Column, Integer, String, ForeignKey
# импортируем модуль для связки таблиц
from sqlalchemy.orm import relationship, backref

# импортируем модель пользователей для связки моделей
from models.users import Users
from data_base.dbcore import Base


class Tempvalue(Base):
    """
    Класс для создания таблицы c временными переменными,
    основан на декларативном стиле SQLAlchemy
    """
    # название таблицы
    __tablename__ = 'tempvalue'
    # поля таблицы
    id = Column(Integer, primary_key=True)
    neww = Column(String)
    on_place = Column(Integer)
    on_word = Column(Integer)
    try_word = Column(String)
    score = Column(Integer)
    tips = Column(Integer)
    tips_word = Column(String)
    count = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    # для каскадного удаления данных из таблицы
    users = relationship(
        Users,
        backref=backref('tempvalue',
                        uselist=True,
                        cascade='delete,all'))
