# импортируем функцию создания объекта бота
from telebot import TeleBot
# импортируем основные настройки проекта
from settings import config
# импортируем главный класс-обработчик бота
from handlers.handler_main import HandlerMain
from settings.logger import Logger
from time import sleep


class TelBot:
    """
    Основной класс телеграмм бота (сервер), в основе которого
    используется библиотека pyTelegramBotAPI
    """
    __version__ = config.VERSION
    __author__ = config.AUTHOR

    def __init__(self):
        """
        Инициализация бота
        """
        # получаем токен
        self.token = config.TOKEN
        # инициализируем бот на основе зарегистрированного токена
        self.bot = TeleBot(self.token)
        # инициализируем логгер
        self.Log = Logger()
        # инициализируем оброботчик событий
        self.handler = HandlerMain(self.bot)


    def start(self):
        """
        Метод предназначен для старта обработчика событий
        """
        self.handler.handle()

    def run_bot(self):
        """
        Метод запускает основные события сервера
        """
        # обработчик событий
        self.start()
        # служит для запуска бота (работа в режиме нон-стоп)
        count_try = 0
        while count_try < 5:
            try:
                self.bot.polling(none_stop=True)
            except:
                self.Log.write_log("Ошибка таймаута")
                count_try += 1
                sleep(15)

        # try:
        #     self.bot.polling(none_stop=True)
        # except:
        #     pass
        # while True:
        #     try:
        #         self.bot.polling(none_stop=True)
        #     except Exception as e:
        #         print(e)
        #         traceback.print_exc()
        #         time.sleep(15)


if __name__ == '__main__':
    bot = TelBot()
    bot.run_bot()
