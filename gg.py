import asyncio, random, datetime
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter, AdminFilter
from aiogram.types import ParseMode
from aiogram.utils import exceptions


class Recruiting:
    def __init__(self, chat_id, max_users=25, timeout=0, description=""):
        self.chat_id = chat_id
        self.max_users = max_users
        self.outtype = 0
        self.maxlen_name = 21
        self.timeout = timeout
        self.rtime = datetime.now()
        self.description = description
        self.users = []
        self.status = "recruiting_started"
        self.msg_id = None
        self.keyboard = None     
        self.smiles = [ '🪂', '🏋️‍♀️', '🤼‍♀️', '🤸‍♀️', '⛹️‍♀️', '🤺', '🤾‍♀️', '🏌🏻‍♀️', '🏇', '🏄🏻‍♀️', '🏊‍♀️', '🤽‍♀️', '🚣‍♂️', '🧗‍♀️', '🚵‍♀️', '🚴‍♀️', '⛷', '🏂']
        
        # Статусы
        self.pattern_msg_status = {
           "recruiting_started": "🎪 Набор участников на розыгрыш начался! ",
           "recruiting_limit_reached": "🚧 Набор участников | завершен успешно (свободных мест нет).",
           "recruiting_timeout": "🚧 Набор участников | завершен успешно (время вышло)."
        }

        # Шаблон сообщения
        self.msg_recruiting = "<b>{pattern_msg_status}</b>\n"
        if self.max_users > 0:
            self.msg_recruiting += "   ◈ Макс. участников: {max_users}\n"
        else:
            self.msg_recruiting += "   ◈ Кол-во участников неограниченно\n"
        if self.timeout > 0:
            self.msg_recruiting += "   ◈ До завершения: {timeout} мин.\n"
        else:
            self.msg_recruiting += "   ◈ Время неограниченно\n"
        if self.description:
            self.msg_recruiting += "\n📜 <b>Описание:</b>\n   — {description}\n"

        self.msg_recruiting += "\n🌒 <b>Список участников:</b>\n{userslist}\n\n"
        
    async def create_joinbtn(self):
        # Создание кнопки
        randEmojNamebtn = random.choice(self.smiles) + " Участвую!"
        self.keyboard = types.InlineKeyboardMarkup(row_width=1)
        self.keyboard.add(
            types.InlineKeyboardButton(
                text=randEmojNamebtn, callback_data="join"
            )
        )

    # Создание сообщения
    async def create_recruiting_message(self, bot):
        await self.create_joinbtn()
        # Отправка сообщения
        msg = await bot.send_message(self.chat_id, self.msg_recruiting.format(
            pattern_msg_status=self.pattern_msg_status[self.status],
            max_users=self.max_users,
            timeout=self.timeout,
            description=self.description,
            userslist=self.get_users_list()
        ), reply_markup=self.keyboard, parse_mode=ParseMode.HTML)

        self.msg_id = msg.message_id

    # Обновление сообщения
    async def update_recruiting_message(self, bot):
        try:
            if self.timeout > 0:
               now = self.rtime
               end_time = now + timedelta(minutes=self.timeout)
               time = datetime(1, 1, 1) + (end_time - now)
               time = time.strftime('%M:%S')
               print(time)
            else:
               time = 0
            await self.create_joinbtn()   
            await bot.edit_message_text(
                self.msg_recruiting.format(
                    pattern_msg_status=self.pattern_msg_status[self.status],
                    max_users=self.max_users,
                    timeout=time,
                    description=self.description,
                    userslist=self.get_users_list()
                ),
                chat_id=self.chat_id,
                message_id=self.msg_id,
                reply_markup=self.keyboard,
                parse_mode=ParseMode.HTML
            )
        except exceptions.MessageNotModified:
            pass

    # Получение списка участников
    def get_users_list(self):
        if self.outtype == 0:
           return "\n".join([f"   {i}. {user}" for i, user in enumerate(self.users, start=1)])
        else:
           return "\n".join([f"  ○ {user}" for user in enumerate(self.users)])

    # Обработка нажатия кнопки "Участвую!"
    async def process_join(self, bot, callback_query: types.CallbackQuery):
        user = callback_query.from_user
        if user.last_name:
            full_name = f"{user.first_name} {user.last_name}"
        else:
            full_name = user.first_name
        # Проверка наличия пользователя в списке участников
        if full_name not in self.users:
            # Добавление пользователя в список участников
            self.users.append(full_name[:self.maxlen_name])

            # Обновление сообщения
            await self.update_recruiting_message(bot)

            # Проверка на достижение лимита пользователей
            if len(self.users) == self.max_users:
                self.status = "recruiting_limit_reached"
                self.keyboard = None

            # Проверка на окончание времени ожидания
            elif self.timeout != 0 and len(self.users) > 0 and len(self.users) < self.max_users:
                await asyncio.sleep(self.timeout * 60)
                if len(self.users) < self.max_users:
                    self.status = "recruiting_timeout"
                    self.keyboard = None

            # Обновление сообщения
            await self.update_recruiting_message(bot)

        # Защита от флуда нажатием кнопки
        try:
            await bot.answer_callback_query(callback_query.id)
        except exceptions.InvalidQueryID:
            pass


class RecruitingManager:
    def __init__(self):
        self.recruitings = {}

    # Обработка команды /gg
    async def cmd_gg(self, bot, message: types.Message):
        chat_id = message.chat.id

        # Получение параметров
        params = message.get_args().split()
        max_users = int(params[0]) if len(params) > 0 else 25
        timeout = int(params[1]) if len(params) > 1 else 0
        description = " ".join(params[2:]) if len(params) > 2 else ""

        # Создание объекта Recruiting
        recruiting = Recruiting(chat_id, max_users, timeout, description)

        # Создание сообщения
        await recruiting.create_recruiting_message(bot)

        # Сохранение объекта Recruiting в словаре
        self.recruitings[chat_id] = recruiting

    # Обработка нажатия кнопки "Участвую!"
    async def process_join(self, bot, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id

        # Получение объекта Recruiting из словаря
        recruiting = self.recruitings.get(chat_id)

        # Проверка наличия объекта Recruiting
        if recruiting is None:
            raise ValueError("Recruiting not found")

        # Обработка нажатия кнопки "Участвую!"
        await recruiting.process_join(bot, callback_query)


# Запуск бота
async def main():
    bot = Bot(token="6059387846:AAFyWIuLjvzieK1sjiRRfB2v47e1UUwNJUo")
    dp = Dispatcher(bot)
    recruiting_manager = RecruitingManager()
    allowed_users = [
        6112710364, 
        5343681896, 
        274918556
    ]
    # Обработка команды /gg
    @dp.message_handler(commands=["gg"])
    async def cmd_gg(message: types.Message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        # Проверка, что сообщение пришло из группового чата
        print(message.chat.type)
        if message.chat.type != 'supergroup':
            await message.answer("⚠️ Команда /gg работает только в групповых чатах.")
            return

        # Проверка, что отправитель сообщения является администратором группы
        chat_member = await bot.get_chat_member(chat_id, user_id)
        if not chat_member.is_chat_admin() and not user_id in allowed_users:
            await message.answer("⚠️ Команда /gg может быть выполнена только администратором группы.")
            return
        await recruiting_manager.cmd_gg(bot, message)

    # Обработка нажатия кнопки "Участвую!"
    @dp.callback_query_handler(lambda c: c.data == "join")
    async def process_join(callback_query: types.CallbackQuery):
        await recruiting_manager.process_join(bot, callback_query)

    # Запуск бота
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
