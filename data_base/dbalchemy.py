from os import path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from data_base.dbcore import Base

from settings import config
from models.users import Users
from models.stats import Stats
from models.settings import Settings
from models.boolset import Boolset
from models.tempvalue import Tempvalue

from settings import utility


class Singleton(type):
    """
    Патерн Singleton предоставляет механизм создания одного
    и только одного объекта класса,
    и предоставление к нему глобальной точки доступа.
    """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class DBManager(metaclass=Singleton):
    """
    Класс-менеджер для работы с БД
    """

    def __init__(self):
        """
        Инициализация сессии и подключения к БД
        """
        self.engine = create_engine(config.DATABASE)
        session = sessionmaker(bind=self.engine)
        self._session = session()
        if not path.isfile(config.DATABASE):
            Base.metadata.create_all(self.engine)


    def close(self):
        """
        Закрывает сесию
        """
        self._session.close()



    def select_all_user_id(self):
        result = self._session.query(Users.id).all()
        self.close()
        return result

    def select_user_id(self, user):
        """
        Возвращает id пользователя в БД или создает нового.
        """
        if self.find_user(user):
            result = self._session.query(
                Users.id).filter_by(teleid=user).one()
            self.close()
        else:
            self.add_user("User" + str(user)[:4], user)
            result = self._session.query(
                Users.id).filter_by(teleid=user).one()
            self.close()
        return result.id

    def add_stats(self, score, games, trys, tips, teleid):
        '''
        Записывает статистику игрока в БД после победы
        '''
        userid = self.select_user_id(teleid)
        if bool(self.find_score(userid)):
            oldscore = self._session.query(Stats.score).filter_by(user_id=userid).one()
            oldgames = self._session.query(Stats.games).filter_by(user_id=userid).one()
            oldtrys = self._session.query(Stats.trys).filter_by(user_id=userid).one()
            oldtips = self._session.query(Stats.tips).filter_by(user_id=userid).one()
            print(oldscore, oldgames, oldtrys, oldtips)
            userstats = Stats(score=oldscore[0]+score, games=oldgames[0]+games, trys= oldtrys[0]+trys, tips = oldtips[0]+tips,
                          user_id=userid)
            self._session.query(Stats).filter_by(user_id=userid).delete()
        else:
            userstats = Stats(score=score, games=1, trys=trys, tips = tips,
                          user_id=userid)
        self._session.add(userstats)
        self._session.commit()
        self.close()

    def add_user(self, name, teleid):
        '''
        Добавляет нового игрока в БД
        '''
        user = Users(name=name, teleid=teleid, is_activ= 1)
        self._session.add(user)
        self._session.commit()
        self.close()

    def update_user_name(self, uname, teleid):
        """
        Обновляет имя указанного пользователя
        """
        self._session.query(Users).filter_by(
            teleid=teleid).update({Users.name: uname})
        self._session.commit()
        self.close()

    def find_user(self, teleid):
        '''
        Ищет игрока, прикладная функция для других методов
        '''
        result = self._session.query(Users).filter_by(
            teleid=teleid).all()

        self.close()
        return result

    def find_score(self, userid):
        '''
        Ищет очки игрока, прикладная функция для других методов
        '''
        result = self._session.query(Stats).filter_by(
            user_id=userid).all()
        self.close()
        return result

    def find_settings(self, userid):
        '''
        Ищет настройки игрока, прикладная функция для других методов
        '''
        result = self._session.query(Settings).filter_by(
            user_id=userid).all()
        self.close()
        return result


    def score_list(self):
        '''
        Возращает рейтинг набранных очков для игроков сыграших более 10 игр
        '''
        articles = self._session.query(Users.name, Stats.score).join(Stats).filter(Stats.games > 10).order_by(Stats.score.desc()).all()
        self.close()
        scorelist = []
        for article in articles:
            scorelist.append(article)
        return scorelist


    def games_list(self):
        '''
        возвращает статистику игр для игроков сыгравших более 10 раз
        '''
        articles = self._session.query(Users.name, Stats.games).join(Stats).filter(Stats.games > 10).order_by(Stats.games.desc()).all()
        self.close()
        scorelist = []
        for article in articles:
            scorelist.append(article)
        return scorelist


    def find_user_name(self, teleid):
        '''
        ищет имя пользователя
        '''
        result = self._session.query(Users.name).filter_by(teleid=teleid).one()
        self.close()
        return result

    def your_score(self, teleid):
        '''
        возвращает статистику игрока
        '''
        userid = self.select_user_id(teleid)
        name = self._session.query(Users.name).filter_by(teleid=teleid).one()
        if bool(self.find_score(userid)):
            score = self._session.query(Stats.score).join(Users).filter_by(teleid=teleid).one()
            games = self._session.query(Stats.games).join(Users).filter_by(teleid=teleid).one()
            trys = self._session.query(Stats.trys).join(Users).filter_by(teleid=teleid).one()
            tips = self._session.query(Stats.tips).join(Users).filter_by(teleid=teleid).one()
            self.close()
            result = f"📊 <b>Твоя статистика</b>: \n\n⚜️<b>{name[0]}</b>\n\n🏅 Количество очков: {score[0]}\n🕹 Игр сыграно: {games[0]}\n🎲 Попыток угадать слово: {trys[0]}\n🏳️ Использовано подсказок: {tips[0]}"
        else:
            result = f"📊 <b>Твоя статистика</b>: \n\n⚜️<b>{name[0]}</b>\n\n🏅 Количество очков: 0\n🕹 Игр сыграно: 0\n🎲 Попыток угадать слово: 0\n🏳️ Использовано подсказок: 0"
        return result

    def show_count_games(self, teleid):
        '''
        Возвращает кол-во проведенных игроком игр
        '''
        userid = self.select_user_id(teleid)
        if bool(self.find_score(userid)):
            games = self._session.query(Stats.games).join(Users).filter_by(teleid=teleid).one()
        return games[0]



    def make_settings(self, teleid):
        '''
        Создает настройки при первом появлении пользователя
        '''
        userid = self.select_user_id(teleid)
        if not bool(self.find_settings(userid)):
            settings = Settings(hard=1, lang="EN", user_id=userid)
            self._session.add(settings)
            self._session.commit()
            self.close()




    def set_bool(self, boolset, value, teleid):
        '''
        Записывает в таблицу bool значения для play (идет ли игра) и name (режим установки имени)
        ждет boolset = "play" или "name" и value True или False
        '''
        userid = self.select_user_id(teleid)
        bultry = self._session.query(Boolset.user_id).filter_by(user_id=userid).all()
        self.close()
        #проверяем есть ли вообще запись в БД, если нет создаем со значениями по дефолту
        if not bultry:
            boolsets = Boolset(name=False, play=False, user_id=userid)
            self._session.add(boolsets)
            self._session.commit()
            self.close()
        if boolset == "play":
            self._session.query(Boolset).filter_by(
            user_id=userid).update({Boolset.play: value})
        elif boolset == "name":
            self._session.query(Boolset).filter_by(
            user_id=userid).update({Boolset.name: value})
        self._session.commit()
        self.close()

    def show_name_set(self, teleid):
        '''
        Возвращает булевое значение можно ли игроку вводить имя
        '''
        #запрашиваем userid для переданного теле id и попутно если нет создаем такого пользователя в в БД
        userid = self.select_user_id(teleid)
        result = self._session.query(Boolset.name).filter_by(user_id=userid).all()
        self.close()
        if result:
            result = result[0][0]
        return result

    def show_play_set(self, teleid):
        '''
        Возвращает булевое значение идет ли сейчас игра
        '''
        #запрашиваем userid для переданного теле id и попутно если нет создаем такого пользователя в в БД
        userid = self.select_user_id(teleid)
        result = self._session.query(Boolset.play).filter_by(user_id=userid).all()
        self.close()
        if result:
            result = result[0][0]
        return result


    def set_settings(self, name, value, teleid):
        userid = self.select_user_id(teleid)
        if name == "lang":
            self._session.query(Settings).filter_by(
            user_id=userid).update({Settings.lang: value})
        elif name == "hard":
            if value in (1, 2, 3):
                self._session.query(Settings).filter_by(
                user_id = userid).update({Settings.hard: value})
        self._session.commit()
        self.close()

    def show_settings(self, name, teleid):
        '''
        Возвращает сложность или язык игры для переданного игрока
        '''
        #запрашиваем userid для переданного теле id и попутно если нет создаем такого пользователя в в БД
        userid = self.select_user_id(teleid)
        self.make_settings(teleid)
        if name == "hard":
            result = self._session.query(Settings.hard).filter_by(user_id=userid).one()
        elif name == "lang":
            result = self._session.query(Settings.lang).filter_by(user_id=userid).one()
        self.close()
        return result[0]

    # def set_lang(self, teleid, lang):
    #     '''
    #     установка языка
    #     '''
    #     userid = self.select_user_id(teleid)
    #     print(userid)
    #     self._session.query(Settings).filter_by(
    #         user_id=userid).update({Settings.lang: lang})
    #     self._session.commit()
    #     self.close()
    #
    #
    # def set_hard(self, teleid, hard):
    #     userid = self.select_user_id(teleid)
    #     self.make_settings(teleid)
    #     if hard in (1, 2, 3):
    #         self._session.query(Settings).filter_by(
    #         user_id = userid).update({Settings.hard: hard})
    #         self._session.commit()
    #         self.close()
    #
    # def show_hard(self, teleid):
    #     '''
    #     Возвращает сложность игры для переданного игрока
    #     '''
    #     #запрашиваем userid для переданного теле id и попутно если нет создаем такого пользователя в в БД
    #     userid = self.select_user_id(teleid)
    #     self.make_settings(teleid)
    #     result = self._session.query(Settings.hard).filter_by(user_id=userid).one()
    #     self.close()
    #     return result[0]
    #
    # def show_lang(self, teleid):
    #     '''
    #     Возвращает язык игры для переданного игрока
    #     '''
    #     #запрашиваем userid для переданного теле id и попутно если нет создаем такого пользователя в в БД
    #     userid = self.select_user_id(teleid)
    #     self.make_settings(teleid)
    #     result = self._session.query(Settings.lang).filter_by(user_id=userid).one()
    #     self.close()
    #     return result


    def set_temp(self, name, value, teleid):
        '''
        устанавливает временные переменные
        '''
        userid = self.select_user_id(teleid)
        proba = self._session.query(Tempvalue.user_id).filter_by(user_id=userid).all()
        self.close()
        if not proba:
            settemp = Tempvalue(neww = "", on_place = 0, on_word = 0, try_word = "", score = 0, tips = 0, tips_word = "", count = 0, user_id=userid)
            self._session.add(settemp)
            self._session.commit()
            self.close()
        if name == "on_place":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.on_place: value})
        elif name == "on_word":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.on_word: value})
        elif name == "neww":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.neww: value})
        elif name == "try_word":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.try_word: value})
        elif name == "score":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.score: value})
        elif name == "tips":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.tips: value})
        elif name == "count":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.count: value})
        elif name == "tips_word":
            self._session.query(Tempvalue).filter_by(
            user_id=userid).update({Tempvalue.tips_word: value})
        else:
            return -1
        self._session.commit()
        self.close()

    def show_temp(self, name, teleid):
        '''
        отдает временные переменные для конкретной игры
        '''
        userid = self.select_user_id(teleid)
        proba = self._session.query(Tempvalue.user_id).filter_by(user_id=userid).all()
        self.close()
        if not proba:
            settemp = Tempvalue(neww = "", on_place = 0, on_word = 0, try_word = "", score = 0, tips = 0, tips_word = "", count = 0, user_id=userid)
            self._session.add(settemp)
            self._session.commit()
            self.close()
        if name == "on_place":
            result = self._session.query(Tempvalue.on_place).filter_by(user_id=userid).one()
        elif name == "neww":
            result = self._session.query(Tempvalue.neww).filter_by(user_id=userid).one()
        elif name == "on_word":
            result = self._session.query(Tempvalue.on_word).filter_by(user_id=userid).one()
        elif name == "try_word":
            result = self._session.query(Tempvalue.try_word).filter_by(user_id=userid).one()
        elif name == "score":
            result = self._session.query(Tempvalue.score).filter_by(user_id=userid).one()
        elif name == "tips":
            result = self._session.query(Tempvalue.tips).filter_by(user_id=userid).one()
        elif name == "count":
            result = self._session.query(Tempvalue.count).filter_by(user_id=userid).one()
        elif name == "tips_word":
            result = self._session.query(Tempvalue.tips_word).filter_by(user_id=userid).one()
        else:
            return -1
        self.close()
        return result[0]












