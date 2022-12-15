# импортируем специальные типы телеграм бота для создания элементов интерфейса
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# импортируем настройки и утилиты
from settings import config
# импортируем класс-менеджер для работы с библиотекой
from data_base.dbalchemy import DBManager
from emoji import emojize


class Keyboards:
    """
    Класс Keyboards предназначен для создания и разметки интерфейса бота
    """
    # инициализация разметки

    def __init__(self):
        self.markup = None
        # инициализируем менеджер для работы с БД
        self.BD = DBManager()

    def set_btn(self, name, step=0, quantity=0, userid=0):
        """
        Создает и возвращает кнопку по входным параметрам
        """
        if name == 'AMOUNT_ORDERS':
            config.KEYBOARD['AMOUNT_ORDERS'] = f"{step + 1} из {str(self.BD.count_rows_order())}"

        if name == 'AMOUNT_PRODUCT':
            config.KEYBOARD['AMOUNT_PRODUCT'] = f"{quantity}"

        if name == 'HARD':
            config.KEYBOARD['HARD'] = emojize(f'📈 Сложность {self.BD.show_settings("hard", userid)} из 3')

        return KeyboardButton(config.KEYBOARD[name])


    def start_menu(self):
        '''
        создаем разметку кнопок в основном меню
        '''
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = self.set_btn('PLAY_NOW')
        itm_btn_2 = self.set_btn('INFO')
        itm_btn_3 = self.set_btn('RANK')
        itm_btn_4 = self.set_btn('SETTINGS')
        # располагаем кнопки в меню
        self.markup.row(itm_btn_1)
        self.markup.row(itm_btn_2, itm_btn_3, itm_btn_4)
        return self.markup

    def rank_menu(self):
        '''
        создаем разметку кнопок в основном меню
        '''
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = self.set_btn('SCORE')
        itm_btn_2 = self.set_btn('ABSSCRE')
        itm_btn_3 = self.set_btn('GAMES')
        itm_btn_4 = self.set_btn('<<')
        itm_btn_5 = self.set_btn('YOURSTATS')
        # располагаем кнопки в меню
        self.markup.row(itm_btn_1, itm_btn_3)
        self.markup.row(itm_btn_2, itm_btn_5)
        self.markup.row(itm_btn_4)
        return self.markup

    def info_menu(self):
        '''
        создаем разметку кнопок в основном меню info
        '''
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = self.set_btn('<<')
        # располагаем кнопки в меню
        self.markup.row(itm_btn_1)
        return self.markup

    def settings_menu(self, userid):
        '''
        создаем разметку кнопок в основном меню settings
        '''
        self.markup = ReplyKeyboardMarkup(True, True)

        if self.BD.show_settings("lang", userid) == "RU":
            itm_btn_1 = self.set_btn('LANGRU')
        elif self.BD.show_settings("lang", userid) == "EN":
            itm_btn_1 = self.set_btn('LANGEN')
        else:
            itm_btn_1 = self.set_btn('X')
        itm_btn_2 = self.set_btn('HARD', userid=userid)
        itm_btn_3 = self.set_btn('CHANGE_NAME')
        itm_btn_4 = self.set_btn('<<')
        # располагаем кнопки в меню
        self.markup.row(itm_btn_1, itm_btn_2)
        self.markup.row(itm_btn_3, itm_btn_4)
        return self.markup

    def remove_menu(self):
        '''
        удаляем старое меню
        '''

        return ReplyKeyboardRemove()

    def game_menu(self):
        '''
        создаем разметку кнопок в основном меню игры
        '''
        self.markup = ReplyKeyboardMarkup(True, True)
        self.markup.add(self.set_btn('RELOAD'))
        self.markup.row(self.set_btn('END_GAME'), self.set_btn('TIPS'))
        # располагаем кнопки в меню
        return self.markup

    def set_inline_btn(self, name, hard):
        '''
        :param name: имя кнопки
        :return: возвращаем созданную инлайн кнопку
        '''

        return InlineKeyboardButton(str(name),
                                    callback_data=str(hard))


    def set_select_diff(self, hard):
        '''
        Создает разметку инлайн кнопок
        :param hard: уровень сложности
        :return: возвращает список кнопок
        '''
        self.markup = InlineKeyboardMarkup(row_width=1)
        '''
        загружаем в названия инлайн кнопок данные из БД в соответствии с категорией товара
        '''
        for i in range(1, 4):
            if i == hard:
                self.markup.add(self.set_inline_btn(emojize(f":radio_button:Уровень сложности {i}"), i))
            else:
                self.markup.add(self.set_inline_btn(emojize(f":white_circle:Уровень сложности {i}"), i))

        return self.markup


