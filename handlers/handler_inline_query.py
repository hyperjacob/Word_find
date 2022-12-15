# импортируем класс родитель
from handlers.handler import Handler
# импортируем сообщения пользователю
from settings.message import MESSAGES

from settings import config


class HandlerInlineQuery(Handler):
    """
    Класс обрабатывает входящие текстовые
    сообщения от нажатия на инлайн-кнопоки
    """

    def __init__(self, bot):
        super().__init__(bot)

    def pressed_btn_level(self, call, code):
        """
        Обрабатывает входящие запросы на нажатие inline-кнопок товара
        """
        # config.HARD = code
        # print('config.HARD ', config.HARD)
        self.BD.set_settings("hard", code, call.from_user.id)
        self.bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        self.bot.send_message(call.from_user.id, f'Уровень сложности изменен на {code}й',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu(call.from_user.id))

    def handle(self):
        # обработчик(декоратор) запросов от нажатия на кнопки товара.
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            code = call.data
            if code.isdigit():
                code = int(code)
            print(code)
            print(call)

            self.pressed_btn_level(call, code)
