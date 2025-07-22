from typing import Union
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from DB.users_sqlite import Database
from config_data.config import config, bot
from utils import format_string
from handlers.callbacks_data import CutMessageCallBack
from models import models


async def get_users_by_page(user_id: int, page: int = 1, message_id: Union[int, None] = None):
    with Database() as db:
        users = db.get_all_users()
        txt = f'Всего пользователей: <b>{len(users)}</b>\n\n'
        for user in users:
            query_amount = len(db.get_user_queries(user.user_id))
            emoji = '🐥'
            if query_amount > 100:
                emoji = '🤯'
            elif query_amount > 5:
                emoji = '😎'
            line = (f'<b>{"@" + user.username if user.username else "🐸"}</b> | <i>{user.user_id}</i> |' +
                    (' 👑 |' if user.is_admin else '') + f' {emoji} {query_amount} [{user.registration_date.strftime("%d.%m.%Y")}]')
            txt += line
        txt = format_string.split_text(txt, config.tg_bot.message_max_symbols)
        if not message_id:
            await bot.send_message(chat_id=user_id, text=txt[page - 1], reply_markup=page_keyboard(action=1, page=page, max_page=len(txt)))
        else:
            await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=txt[page - 1],
                                        reply_markup=page_keyboard(action=1, page=page, max_page=len(txt)))


async def user_query_by_page(user_id: int, user_id_to_find: Union[int, None], page: int = 1, message_id: Union[int, None] = None):
    with Database() as db:
        queries = (db.get_user_queries(user_id_to_find))
        if not user_id_to_find or not queries:
            await bot.send_message(chat_id=user_id, text='Неправильный <i>user_id</i> или этот пользователь не отправлял запросы')
            return
        username = db.get_user(user_id_to_find).username
        txt = f'История запросов <b>{"@" + username if username else user_id_to_find}</b>\n\n'
        query: models.Query
        for query in queries:
            query_time = query.query_date if query.query_date else '❓'
            user_query = format_string.format_string(query.query_text).replace("\n", "\t")
            line = f'[{query_time}]: <blockquote>{user_query}</blockquote>\n\n'
            if len(line) + len(txt) < 4096:
                txt += line
        txt = format_string.split_text(txt, config.tg_bot.message_max_symbols)
        if not message_id:
            await bot.send_message(chat_id=user_id, text=txt[page - 1].replace('\t', '\n'),
                                   reply_markup=page_keyboard(action=2, page=page, max_page=len(txt), user_id=user_id_to_find))
        else:
            await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=txt[page - 1].replace('\t', '\n'),
                                        reply_markup=page_keyboard(action=2, page=page, max_page=len(txt), user_id=user_id_to_find))


def page_keyboard(action: int, page: int, max_page: int, user_id: int = 0):
    array_buttons: list[list[InlineKeyboardButton]] = [[]]
    if page > 1:
        array_buttons[0].append(
            InlineKeyboardButton(text='<', callback_data=CutMessageCallBack(action=action, page=page - 1, user_id=user_id).pack())
        )
    array_buttons[0].append(
        InlineKeyboardButton(text=str(page), callback_data=CutMessageCallBack(action=-1).pack())
    )
    if page < max_page:
        array_buttons[0].append(
            InlineKeyboardButton(text='>', callback_data=CutMessageCallBack(action=action, page=page + 1, user_id=user_id).pack())
        )
    if len(array_buttons[0]) == 1:
        return None
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup
