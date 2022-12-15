from settings.message import MESSAGES
from handlers.handler import Handler
from settings import config
from settings import utility
from emoji import emojize
from random import randint


class HendlerAllText(Handler):
    # класс обрабатывает входящие текстовые сообщения от нажатия на кнопку

    def __int__(self, bot):
        super().__init__(bot)
        # шаг в заказе
        self.step = 0

    def new_word_gen(self, message):
        '''
        генератор нового слова
        '''
        #генерируем слово в
        self.BD.set_temp("neww", config.newword(self.BD.show_settings("lang", message.from_user.id), self.BD.show_settings("hard", message.from_user.id)), message.from_user.id)
        # config.neww = {message.from_user.id: config.newword(self.BD.show_lang(message.from_user.id)[0], self.BD.show_hard(message.from_user.id))}
        self.BD.set_temp("count", 1, message.from_user.id)
        self.BD.set_temp("tips_word", "", message.from_user.id)
        self.BD.set_temp("tips", 3, message.from_user.id)
        self.BD.set_temp("score", len(self.BD.show_temp("neww", message.from_user.id)) * 100, message.from_user.id)
        print("neww: ", self.BD.show_temp("neww", message.from_user.id), "count ", self.BD.show_temp("count", message.from_user.id), "score ", self.BD.show_temp("score", message.from_user.id))

    def pressed_btn_play(self, message):
        '''
        обработка сообщений от нажатия кнопки играть
        '''
        self.new_word_gen(message)
        self.BD.set_bool('play', True, message.from_user.id)
        print(self.BD.show_play_set(message.from_user.id))
        self.bot.send_message(message.chat.id,
                              emojize(f'🎮<b>Начнем игру!</b>\nЯ загадал слово из {len(self.BD.show_temp("neww", message.from_user.id))} букв'),
                              parse_mode="HTML",
                              reply_markup=self.keybords.game_menu())


    def successful(self, message):
        '''
        действия при выигрыше
        '''
        self.BD.set_bool('play', False, message.from_user.id)
        self.BD.add_stats(self.BD.show_temp("score", message.from_user.id), 1, self.BD.show_temp("count", message.from_user.id), (3 - self.BD.show_temp("tips", message.from_user.id)), message.from_user.id)
        if int(str(self.BD.show_temp('count', message.from_user.id))[:1]) == 1:
            tr = "попытку"
        elif int(str(self.BD.show_temp('count', message.from_user.id))[:1]) in [2,3,4]:
            tr = "попытки"
        else:
            tr = "попыток"
        self.bot.send_message(message.chat.id,
                                      emojize(f"🎆Молодец, ты угадал слово за <b>{self.BD.show_temp('count', message.from_user.id)}</b> {tr}🎲\nи заработал <b>{self.BD.show_temp('score', message.from_user.id)}</b> очков🏅! Хочешь сыграть еще?"),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
        if self.BD.show_count_games(message.from_user.id) == 100:
            self.bot.send_message(message.chat.id,
                                      emojize(f'🏆Новое достижение: 🕹<b>"100 игр вместе</b>"\n🏅Ты заработал дополнительно <b>1000</b> очков!)'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
            self.BD.add_stats(1000, 0, 0, 0, message.from_user.id)
        if self.BD.show_count_games(message.from_user.id) == 500:
            self.bot.send_message(message.chat.id,
                                      emojize(f'🏆Новое достижение: <b>"500 игр вместе"</b>🕹\n🏅Ты заработал дополнительно <b>5000</b> очков!'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
            self.BD.add_stats(5000, 0, 0, 0, message.from_user.id)
        if self.BD.show_count_games(message.from_user.id) == 1000:
            self.bot.send_message(message.chat.id,
                                      emojize(f'🏆Новое достижение: 🕹<b>"1000 игр вместе"</b>\n🏅Ты заработал дополнительно <b>10000</b> очков!'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
            self.BD.add_stats(10000, 0, 0, 0, message.from_user.id)
        self.BD.set_temp("score", 0, message.from_user.id)
        self.BD.set_temp("count", 1, message.from_user.id)
        self.BD.set_temp("tips", 3, message.from_user.id)

    def nice_try(self, message):
         #дейстаия при попытке если было введено слово нужного числа букв
        for i in range(len(message.text)):
            if message.text[i].lower() == self.BD.show_temp("neww", message.from_user.id)[i]:
                        #условие - если буква загаданного слова на iй позиции совпадает с буковой введенного слова на iй позиции, то прибавляется 1 к "буквам на своем месте"
                self.BD.set_temp("on_place", self.BD.show_temp("on_place", message.from_user.id)+1, message.from_user.id)
            if message.text[i].lower() in self.BD.show_temp("neww", message.from_user.id) and message.text[i].lower() not in self.BD.show_temp("try_word", message.from_user.id):
                        # исключаем ситуации, при которых буква в введенном слове мб повторяться, мы должны учесть ровно столько раз, сколько она в угадываемом. Поэтому добавляем букву в массив букв, которые уже проверялись
                self.BD.set_temp("try_word", self.BD.show_temp("try_word", message.from_user.id)+message.text[i].lower(), message.from_user.id)
                for w in self.BD.show_temp("neww", message.from_user.id):
                            # а теперь обратная ситуация: мб в угадываемом слове несколько одинаковых букв, нужно это учесть
                    if w == message.text[i].lower():
                        self.BD.set_temp("on_word", self.BD.show_temp("on_word", message.from_user.id)+1, message.from_user.id)
        self.bot.send_message(message.chat.id,
                                      emojize(f'🔡Букв в слове: {self.BD.show_temp("on_word", message.from_user.id)}, на своем месте: {self.BD.show_temp("on_place", message.from_user.id)}'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.game_menu())
        self.BD.set_temp("count", self.BD.show_temp("count", message.from_user.id)+1, message.from_user.id)
        if self.BD.show_temp("score", message.from_user.id) > (self.BD.show_settings("hard", message.from_user.id) * 10):
            self.BD.set_temp("score", self.BD.show_temp("score", message.from_user.id) - self.BD.show_settings("hard", message.from_user.id) * 10, message.from_user.id)
        self.BD.set_temp("on_place", 0, message.from_user.id)
        self.BD.set_temp("on_word", 0, message.from_user.id)
        self.BD.set_temp("try_word", "", message.from_user.id)
        print(self.BD.show_temp("neww", message.from_user.id))

    def bed_try(self, message):
        '''
        При вводе слова с другим кол-вом букв
        '''
        if self.BD.show_temp("score", message.from_user.id) > (self.BD.show_settings("hard", message.from_user.id) * 10):
            self.BD.set_temp("score", self.BD.show_temp("score", message.from_user.id) - self.BD.show_settings("hard", message.from_user.id) * 10, message.from_user.id)
        self.BD.set_temp("count", self.BD.show_temp("count", message.from_user.id)+1, message.from_user.id)
        self.bot.send_message(message.chat.id, emojize(f'🛑Слово должно быть из {len(self.BD.show_temp("neww", message.from_user.id))} букв'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.game_menu())

    def tips_enter(self, message):
        if self.BD.show_temp("tips", message.from_user.id) > 0:
            if self.BD.show_temp("score", message.from_user.id) > 100:
                self.BD.set_temp("score", self.BD.show_temp("score", message.from_user.id) - 100, message.from_user.id)
            else:
                self.BD.set_temp("score", 0, message.from_user.id)
            long = len(self.BD.show_temp("neww", message.from_user.id))
            if self.BD.show_temp("tips_word", message.from_user.id) == "":
                word = ""
                for i in range(1, len(self.BD.show_temp("neww", message.from_user.id))+1):
                    word += "*"
                self.BD.set_temp("tips_word", word, message.from_user.id)
            while True:
                num_word = randint(0, long-1)
                print(num_word, self.BD.show_temp("neww", message.from_user.id)[num_word])
                if self.BD.show_temp("neww", message.from_user.id)[num_word] not in self.BD.show_temp("tips_word", message.from_user.id):
                    self.BD.set_temp("tips", self.BD.show_temp("tips", message.from_user.id) -1, message.from_user.id)
                    for i in range(0, len(self.BD.show_temp("neww", message.from_user.id))):
                        if i == num_word:
                            word = self.BD.show_temp("tips_word", message.from_user.id)
                            result = word[:i] + self.BD.show_temp("neww", message.from_user.id)[num_word] + word[i+1:]
                            self.BD.set_temp("tips_word", result, message.from_user.id)
                    break
            self.bot.send_message(message.chat.id, emojize(f':white_flag:Ваша подсказка: {self.BD.show_temp("tips_word", message.from_user.id)}'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.game_menu())
        else:
            self.bot.send_message(message.chat.id, emojize(f'У вас недостаточно подсказок'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.game_menu())










    def pressed_btn_reload(self, message):
        '''
        обработка сообщений от нажатия кнопки перезапустить игру
        '''
        self.new_word_gen(message)
        self.BD.set_bool('play', False, message.from_user.id)
        self.bot.send_message(message.chat.id,
                              f'Я загадал новое слово! В нем {len(self.BD.show_temp("neww", message.from_user.id))} букв',
                              parse_mode="HTML",
                              reply_markup=self.keybords.game_menu())
        self.BD.set_bool('play', True, message.from_user.id)

    def pressed_btn_info(self, message):
        '''
        обработка сообщений от нажатия кнопки info
        '''
        self.bot.send_message(message.chat.id, MESSAGES['onboard'],
                              parse_mode="HTML",
                              reply_markup=self.keybords.info_menu())

    def pressed_btn_settings(self, message):
        '''
        обработка сообщений от нажатия кнопки settings
        '''
        self.BD.show_settings("hard", message.from_user.id)
        self.BD.make_settings(message.from_user.id)
        self.bot.send_message(message.chat.id, MESSAGES['settings'],
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))

    def pressed_btn_rank(self, message):
        '''
        обработка сообщений от нажатия кнопки зал славы
        '''
        self.bot.send_message(message.chat.id, emojize(
            '🏆 Добро пожаловать в Зал славы! \nСюда попадают игроки сыгравшие не менее 10 игр!'),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_langen(self, message):
        '''
        обработка сообщений от нажатия кнопки смены языка
        '''
        self.BD.set_settings("lang", "EN", message.from_user.id)
        self.bot.send_message(message.chat.id, 'Вы изменили язык на английский',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))

    def pressed_btn_langru(self, message):
        '''
        обработка сообщений от нажатия кнопки смены языка
        '''
        self.BD.set_settings("lang", "RU", message.from_user.id)
        self.bot.send_message(message.chat.id, 'Вы изменили язык на русский',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))

    def pressed_btn_back(self, message):
        '''
        обработка сообщений от нажатия кнопки back
        '''
        self.bot.send_message(message.chat.id, 'Вы вернулись назад',
                              parse_mode="HTML",
                              reply_markup=self.keybords.start_menu())

    def pressed_btn_end(self, message):
        '''
        кнопка закончить игру
        '''
        self.BD.set_bool('play', False, message.from_user.id)
        self.BD.set_temp("score", 0, message.from_user.id)
        self.BD.set_temp("count", 1, message.from_user.id)
        self.BD.set_temp("tips", 3, message.from_user.id)
        self.bot.send_message(message.chat.id, 'Вы закончили игру',
                              parse_mode="HTML",
                              reply_markup=self.keybords.start_menu())

    def pressed_btn_diff(self, message, diff):
        print('message', message)
        self.bot.send_message(message.chat.id, 'Выберите сложность:',
                              reply_markup=self.keybords.set_select_diff(diff))
        # self.bot.send_message(message.chat.id,"",
        #                       reply_markup=self.keybords.settings_menu())
        print('message', message)

    def pressed_btn_login(self, message):
        self.BD.set_bool("name", True, message.from_user.id)
        self.bot.send_message(message.chat.id, 'Введите свое имя',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))

    def win_stats(self, message, score, trys, tips):
        pass

    def pressed_btn_score(self, message):
        '''
        Возвращает статистику по очкам
        '''
        scorelist = self.BD.score_list()
        print(scorelist)
        scorestats = "<b>🏅 Общий зачет (по очкам): \n\n</b>"
        i = 1
        userid = self.BD.select_user_id(message.from_user.id)
        for el in scorelist:
            if bool(self.BD.find_score(userid)) and el[0] == self.BD.find_user_name(message.from_user.id)[0]:
                if i > 10:
                    scorestats += '      ...\n'
                scorestats += f'⚜️<b>{i}. {el[0]}:    {el[1]}\n</b>'
            elif i < 11:
                scorestats += f'      {i}. {el[0]}:    {el[1]}\n'
            i += 1
        self.bot.send_message(message.chat.id, emojize(scorestats),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_games(self, message):
        gameslist = self.BD.games_list()
        print(gameslist)
        gamesstats = "<b>🕹 По количеству игр: \n\n</b>"
        i = 1
        userid = self.BD.select_user_id(message.from_user.id)
        for el in gameslist:
            if bool(self.BD.find_score(userid)) and el[0] == self.BD.find_user_name(message.from_user.id)[0]:
                if i > 10:
                    gamesstats += '      ...\n'
                gamesstats += f'⚜️<b>{i}. {el[0]}:    {el[1]}\n</b>'
            elif i < 11:
                gamesstats += f'      {i}. {el[0]}:    {el[1]}\n'
            i += 1
        self.bot.send_message(message.chat.id, emojize(gamesstats),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_abs(self, message):
        gameslist = self.BD.games_list()
        scorelist = self.BD.score_list()
        score_game = []
        for game in gameslist:
            for score in scorelist:
                if game[0] == score[0]:
                    score_game.append((game[0], score[1] / game[1]))
        score_game.sort(reverse=True, key=lambda val: val[1])
        scoregamesstats = "<b>👑 Абсолютный зачет (очки/игры): \n\n</b>"
        i = 1
        userid = self.BD.select_user_id(message.from_user.id)
        for el in score_game:
            if bool(self.BD.find_score(userid)) and el[0] == self.BD.find_user_name(message.from_user.id)[0]:
                if i > 10:
                    scoregamesstats += '      ...\n'
                scoregamesstats += f'⚜️<b>{i}. {el[0]}:    {round(el[1], 2)}\n</b>'
            elif i < 11:
                scoregamesstats += f'      {i}. {el[0]}:    {round(el[1], 2)}\n'
            i += 1
        self.bot.send_message(message.chat.id, emojize(scoregamesstats),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_uscore(self, message):
        mess = self.BD.your_score(message.from_user.id)
        self.bot.send_message(message.chat.id, emojize(mess),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())


    def handle(self):
        '''
        обработчик (декоратор) сообщений
        обрабатывает входящии сообщения от нажатия кнопок
        '''

        @self.bot.message_handler(func=lambda message: True)
        def handle(message):
            # Меню

            if message.text == config.KEYBOARD['PLAY_NOW']:
                self.pressed_btn_play(message)

            if message.text == config.KEYBOARD['INFO']:
                self.pressed_btn_info(message)

            if message.text == config.KEYBOARD['SETTINGS']:
                self.pressed_btn_settings(message)

            if message.text == config.KEYBOARD['RANK']:
                self.pressed_btn_rank(message)

            if message.text == config.KEYBOARD['<<']:
                self.pressed_btn_back(message)

            if message.text == config.KEYBOARD['END_GAME']:
                self.pressed_btn_end(message)

            if message.text == config.KEYBOARD['RELOAD']:
                self.pressed_btn_reload(message)

            # Меню settings

            if message.text == config.KEYBOARD['LANGRU']:
                self.pressed_btn_langen(message)

            if message.text == config.KEYBOARD['LANGEN']:
                self.pressed_btn_langru(message)

            if config.KEYBOARD['HARD'] and message.text == config.KEYBOARD['HARD']:
                self.pressed_btn_diff(message, self.BD.show_settings("hard", message.from_user.id))

            if message.text == config.KEYBOARD['CHANGE_NAME']:
                self.pressed_btn_login(message)

            # Меню Rank

            if message.text == config.KEYBOARD['SCORE']:
                self.pressed_btn_score(message)

            if message.text == config.KEYBOARD['GAMES']:
                self.pressed_btn_games(message)

            if message.text == config.KEYBOARD['ABSSCRE']:
                self.pressed_btn_abs(message)

            if message.text == config.KEYBOARD['YOURSTATS']:
                self.pressed_btn_uscore(message)


            # Авторизация
            if bool(self.BD.show_name_set(message.from_user.id)) and message.text != config.KEYBOARD['CHANGE_NAME'] and message.text != "":
                self.BD.set_bool("name", False, message.from_user.id)
                print(self.BD.find_user(message.from_user.id))
                if bool(self.BD.find_user(message.from_user.id)):
                    self.BD.update_user_name(message.text, message.from_user.id)
                else:
                    username = message.text
                    teleid = message.from_user.id
                    self.BD.add_user(username, teleid)
                self.bot.send_message(message.chat.id, f'Вы изменили имя на {message.text}',
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.settings_menu(message.from_user.id))

            # Игра

            if self.BD.show_play_set(message.from_user.id) and message.text.lower() == self.BD.show_temp("neww", message.from_user.id) and message.text != config.KEYBOARD['TIPS']:
                self.successful(message)



            if self.BD.show_play_set(message.from_user.id) and len(message.text) == len(self.BD.show_temp("neww", message.from_user.id)) and message.text.lower() != self.BD.show_temp("neww", message.from_user.id) and message.text != config.KEYBOARD[
                'PLAY_NOW'] and message.text != config.KEYBOARD['RELOAD'] and message.text != config.KEYBOARD['TIPS']:
                self.nice_try(message)


            if self.BD.show_play_set(message.from_user.id) and len(message.text) != len(self.BD.show_temp("neww", message.from_user.id)) and message.text != config.KEYBOARD[
                'PLAY_NOW'] and message.text != config.KEYBOARD['RELOAD'] and message.text != config.KEYBOARD['TIPS']:
                self.bed_try(message)

            if self.BD.show_play_set(message.from_user.id) and message.text == config.KEYBOARD['TIPS']:
                self.tips_enter(message)

