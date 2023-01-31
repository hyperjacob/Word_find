from settings.message import MESSAGES
from handlers.handler import Handler
from settings import config
from emoji import emojize
from random import randint

class HendlerAllText(Handler):
    # класс обрабатывает входящие текстовые сообщения от нажатия на кнопку
    count = {}
    play = {}
    tips_word = {}
    score = {}
    tips = {}
    neww = {}
    name = {}
    hard = {}

    def __int__(self, bot):
        super().__init__(bot)

    def new_word_gen(self, message):
        '''
        генератор нового слова
        '''
        #генерируем слово в
        try:
            self.hard[message.from_user.id] = self.BD.show_settings("hard", message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось получить сложность")
            self.hard[message.from_user.id] = 1
        self.neww[message.from_user.id] = config.newword(self.BD.show_settings("lang", message.from_user.id), self.hard[message.from_user.id])
        print(self.neww[message.from_user.id])
        self.count[message.from_user.id] = 0
        self.tips_word[message.from_user.id] = ""
        self.score[message.from_user.id] = len(self.neww[message.from_user.id])*100
        self.tips[message.from_user.id] = 3
        self.Log.write_log("word: " + self.neww[message.from_user.id] + ", user id: " + str(message.from_user.id))

    def pressed_btn_play(self, message):
        '''
        обработка сообщений от нажатия кнопки играть
        '''
        self.new_word_gen(message)
        self.play[message.from_user.id] = True
        try:
            if self.BD.show_settings("lang", message.from_user.id) == "RU":
                lang = "на русском языке"
            else:
                lang = "на английском языке"
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось получить язык")
            lang = ""
        self.Log.write_log("Game start. User: " + str(message.from_user.id))
        self.bot.send_message(message.chat.id,
                              emojize(f'🎮<b>Новая игра</b>\n\nЯ загадал слово {lang} из {len(self.neww[message.from_user.id])} букв'),
                              parse_mode="HTML",
                              reply_markup=self.keybords.game_menu())

    def successful(self, message):
        '''
        действия при выигрыше
        '''
        self.count[message.from_user.id] += 1
        self.play[message.from_user.id] = False
        try:
            self.BD.add_stats(self.score.get(message.from_user.id, 0), 1, self.count.get(message.from_user.id, 0), (3 - self.tips.get(message.from_user.id, 3)), message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось записать статистику")
        if int(str(self.count[message.from_user.id])[:1]) == 1:
            tr = "попытку"
        elif int(str(self.count[message.from_user.id])[:1]) in [2,3,4]:
            tr = "попытки"
        else:
            tr = "попыток"
        self.bot.send_message(message.chat.id,
                                      emojize(f"<b>🏆Победа!</b>\n\n 🎆Молодец, ты угадал слово за <b>{self.count[message.from_user.id]}</b> {tr}🎲\nи заработал <b>{self.score[message.from_user.id]}</b> очков🏅! Хочешь сыграть еще?"),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
        try:
            if self.BD.show_count_games(message.from_user.id) == 100:
                self.bot.send_message(message.chat.id,
                                      emojize(f'🏆Новое достижение: 🕹<b>"100 игр вместе</b>"\n🏅Ты заработал дополнительно <b>1000</b> очков!)'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
                self.BD.add_stats(1000, 0, 0, 0, message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось записать статистику")
        try:
            if self.BD.show_count_games(message.from_user.id) == 500:
                self.bot.send_message(message.chat.id,
                                      emojize(f'🏆Новое достижение: <b>"500 игр вместе"</b>🕹\n🏅Ты заработал дополнительно <b>5000</b> очков!'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
                self.BD.add_stats(5000, 0, 0, 0, message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось записать статистику")
        try:
            if self.BD.show_count_games(message.from_user.id) == 1000:
                self.bot.send_message(message.chat.id,
                                      emojize(f'🏆Новое достижение: 🕹<b>"1000 игр вместе"</b>\n🏅Ты заработал дополнительно <b>10000</b> очков!'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.start_menu())
                self.BD.add_stats(10000, 0, 0, 0, message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось записать статистику")
        self.score[message.from_user.id] = 0
        self.count[message.from_user.id] = 0
        self.tips[message.from_user.id] = 3

    def nice_try(self, message):
         #дейстаия при попытке если было введено слово нужного числа букв
        on_place = 0
        on_word = 0
        try_word = ""
        for i in range(len(message.text)):
            if message.text[i].lower() == self.neww[message.from_user.id][i]:
                        #условие - если буква загаданного слова на iй позиции совпадает с буковой введенного слова на iй позиции, то прибавляется 1 к "буквам на своем месте"
                on_place += 1
            if message.text[i].lower() in self.neww[message.from_user.id] and message.text[i].lower() not in try_word:
                        # исключаем ситуации, при которых буква в введенном слове мб повторяться, мы должны учесть ровно столько раз, сколько она в угадываемом. Поэтому добавляем букву в массив букв, которые уже проверялись
                try_word += message.text[i].lower()
                for w in self.neww[message.from_user.id]:
                            # а теперь обратная ситуация: мб в угадываемом слове несколько одинаковых букв, нужно это учесть
                    if w == message.text[i].lower():
                        on_word += 1
        self.bot.send_message(message.chat.id,
                                      emojize(f'🔡Букв в слове: {on_word}, на своем месте: {on_place}'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.game_menu())
        self.count[message.from_user.id] += 1
        try:
            if self.score[message.from_user.id] > (self.hard.get(message.from_user.id, self.BD.show_settings("hard", message.from_user.id)) * 10):
                self.score[message.from_user.id] -= self.hard[message.from_user.id] * 10
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось уменьшить очки при неудачной попытке")

    def bed_try(self, message):
        '''
        При вводе слова с другим кол-вом букв
        '''
        try:
            if self.score.get(message.from_user.id, 0) > self.hard.get(message.from_user.id, self.BD.show_settings("hard", message.from_user.id)) * 10:
                self.score[message.from_user.id] -= self.hard[message.from_user.id] * 10
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось уменьшить очки при неудачной попытке")
        self.count[message.from_user.id] += 1
        self.bot.send_message(message.chat.id, emojize(f'🛑Слово должно быть из {len(self.neww[message.from_user.id])} букв'),
                                      parse_mode="HTML",
                                      reply_markup=self.keybords.game_menu())

    def tips_enter(self, message):
        # при запросе подсказки
        if self.tips.get(message.from_user.id, 3) > 0:
            if self.score[message.from_user.id] > 100:
                self.score[message.from_user.id] -= 100
            else:
                self.score[message.from_user.id] = 0
            long = len(self.neww[message.from_user.id])
            if self.tips_word.get(message.from_user.id, "") == "":
                word = ""
                for i in range(1, len(self.neww[message.from_user.id])+1):
                    word += "*"
                self.tips_word[message.from_user.id] = word
            while True:
                num_word = randint(0, long-1)
                if self.neww[message.from_user.id][num_word] not in self.tips_word.get(message.from_user.id, ""):
                    self.tips[message.from_user.id] -= 1
                    for i in range(0, len(self.neww[message.from_user.id])):
                        if i == num_word:
                            word = self.tips_word.get(message.from_user.id, "")
                            result = word[:i] + self.neww[message.from_user.id][num_word] + word[i+1:]
                            self.tips_word[message.from_user.id] = result
                    break
            self.bot.send_message(message.chat.id, emojize(f':white_flag:Ваша подсказка: {self.tips_word[message.from_user.id]}\n*️⃣Количество оставшихся подсказок: {self.tips[message.from_user.id]}'),
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
        self.play[message.from_user.id] = False
        self.bot.send_message(message.chat.id,
                              f'Я загадал новое слово! В нем {len(self.neww[message.from_user.id])} букв',
                              parse_mode="HTML",
                              reply_markup=self.keybords.game_menu())
        self.play[message.from_user.id] = True

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
        try:
            self.BD.show_settings("hard", message.from_user.id)
            self.BD.make_settings(message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось проверить наличие настроеки и профиля пользователя при входе в настройки")
        self.bot.send_message(message.chat.id, MESSAGES['settings'],
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))

    def pressed_btn_rank(self, message):
        '''
        обработка сообщений от нажатия кнопки зал славы
        '''
        # self.BD.set_mod(4, message.from_user.id)
        try:
            self.bot.send_message(message.chat.id, emojize(
                        f'🏆 Зал славы \n\n<b>Общее количество игроков:</b> {self.BD.users_count()}\n\n\n<i>Сюда попадают игроки, сыгравшие не менее 10 игр</i>'),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось вычислить активное количество игроков")
            self.bot.send_message(message.chat.id, emojize(
                        f'🏆 Зал славы \n\n<i>Сюда попадают игроки, сыгравшие не менее 10 игр</i>'),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_langen(self, message):
        '''
        обработка сообщений от нажатия кнопки смены языка
        '''
        try:
            self.BD.set_settings("lang", "EN", message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удаось поменять язык в настройках")
        self.bot.send_message(message.chat.id, 'Вы изменили язык на английский',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))
        # self.BD.set_bool("btnset", False, message.from_user.id)

    def pressed_btn_langru(self, message):
        '''
        обработка сообщений от нажатия кнопки смены языка
        '''
        try:
            self.BD.set_settings("lang", "RU", message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удаось поменять язык в настройках")
        self.bot.send_message(message.chat.id, 'Вы изменили язык на русский',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))
        # self.BD.set_bool("btnset", False, message.from_user.id)

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
        try:
            self.BD.add_stats(0, 1, self.count.get(message.from_user.id, 0), 3 - self.tips.get(message.from_user.id, 3), message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. Не удалось записать статистику при выходе из игры")
        self.play[message.from_user.id] = False
        self.score[message.from_user.id] = 0
        self.count[message.from_user.id] = 0
        self.tips[message.from_user.id] = 3
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
        # self.BD.set_bool("btnset", False, message.from_user.id)

    def pressed_btn_login(self, message):
        self.name[message.from_user.id] = True
        self.bot.send_message(message.chat.id, 'Введите свое имя',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(message.from_user.id))

    def pressed_btn_score(self, message):
        '''
        Возвращает статистику по очкам
        '''
        try:
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
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удалось загрузить общий зачет")
            scorestats = "None"
        self.bot.send_message(message.chat.id, emojize(scorestats),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_games(self, message):
        try:
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
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удалось загрузить статистику по играм")
            gamesstats = "None"
        self.bot.send_message(message.chat.id, emojize(gamesstats),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_abs(self, message):
        try:
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
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удалось загрузить абсолютную статистику")
            scoregamesstats = "None"
        self.bot.send_message(message.chat.id, emojize(scoregamesstats),
                              parse_mode="HTML",
                              reply_markup=self.keybords.rank_menu())

    def pressed_btn_uscore(self, message):
        try:
            mess = self.BD.your_score(message.from_user.id)
        except:
            self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удалось загрузить статистику игрока")
            mess = "None"
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

            # универсальная кнопка почти для всех меню

            if message.text == config.KEYBOARD['<<']:
                self.pressed_btn_back(message)

            # Главное меню

            if message.text == config.KEYBOARD['PLAY_NOW']:
                self.pressed_btn_play(message)

            if message.text == config.KEYBOARD['INFO']:
                self.pressed_btn_info(message)

            if message.text == config.KEYBOARD['SETTINGS']:
                self.pressed_btn_settings(message)

            if message.text == config.KEYBOARD['RANK']:
                self.pressed_btn_rank(message)

            # Меню игры

            if message.text == config.KEYBOARD['END_GAME']:
                self.pressed_btn_end(message)

            if message.text == config.KEYBOARD['RELOAD']:
                self.pressed_btn_reload(message)

            if message.text == config.KEYBOARD['TIPS']:
                self.tips_enter(message)

            # Игра

            if self.play.get(message.from_user.id, False) and message.text.lower() == self.neww.get(message.from_user.id, "X"):
                self.successful(message)


            if self.play.get(message.from_user.id, False) and len(message.text) == len(self.neww.get(message.from_user.id, "xxxxxxxxxxxxxxxxxxxxxxxxxxxx")) and message.text.lower() != self.neww and message.text != config.KEYBOARD[
                'PLAY_NOW'] and message.text != config.KEYBOARD['RELOAD'] and message.text != config.KEYBOARD['TIPS']:
                self.nice_try(message)


            if self.play.get(message.from_user.id, False) and len(message.text) != len(self.neww[message.from_user.id]) and message.text != config.KEYBOARD[
                'PLAY_NOW'] and message.text != config.KEYBOARD['RELOAD'] and message.text != config.KEYBOARD['TIPS']:
                self.bed_try(message)

            # Меню settings

            if message.text == config.KEYBOARD['LANGRU']:
                self.pressed_btn_langen(message)

            if message.text == config.KEYBOARD['LANGEN']:
                self.pressed_btn_langru(message)

            if config.KEYBOARD['HARD'] and message.text == config.KEYBOARD['HARD']:
                try:
                    self.pressed_btn_diff(message, self.BD.show_settings("hard", message.from_user.id))
                except:
                    self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удалось загрузить сложность для отклика по кнопке")

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
            if self.name.get(message.from_user.id, False) and message.text != config.KEYBOARD['CHANGE_NAME'] and message.text != "":
                self.name[message.from_user.id] = False
                try:
                    if bool(self.BD.find_user(message.from_user.id)):
                        self.BD.update_user_name(message.text, message.from_user.id)
                    else:
                        username = message.text
                        teleid = message.from_user.id
                        self.BD.add_user(username, teleid)
                    self.bot.send_message(message.chat.id, f'Вы изменили имя на {message.text}',
                                          parse_mode="HTML",
                                          reply_markup=self.keybords.settings_menu(message.from_user.id))
                except:
                    self.Log.write_log("user id: " + str(message.from_user.id) + ". Ошибка доступа к БД. не удалось поменять имя игрока")
                    self.bot.send_message(message.chat.id, f'К сожалению, изменить имя в данный момент нельзя',
                                          parse_mode="HTML",
                                          reply_markup=self.keybords.settings_menu(message.from_user.id))
