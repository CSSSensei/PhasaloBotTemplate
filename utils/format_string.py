import re
from typing import List, Optional
from DB.models import UserModel, QueryModel
from phrases import PHRASES_RU


def clear_string(text: str):
    if not text:
        return '⬛️'
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")


def find_first_number(input_string):
    match = re.search(r'\d+', input_string)

    if match:
        return int(match.group())
    else:
        return None


def split_text(text, n):
    result = []
    lines = text.split('\n')
    current_chunk = ''
    current_length = 0

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= n:  # Check if adding the line and '\n' fits in the chunk
            if current_chunk:  # Add '\n' if it's not the first line in the chunk
                current_chunk += '\n'
            current_chunk += line
            current_length += len(line) + 1
        else:
            result.append(current_chunk)
            current_chunk = line
            current_length = len(line)

    if current_chunk:
        result.append(current_chunk)

    return result


def get_query_count_emoji(count: int) -> str:
    for emoji, threshold in PHRASES_RU.icon.query.thresholds.item():
        if count > threshold:
            return emoji
    return PHRASES_RU.icon.query.default


def format_user_list(users_info: List[UserModel]) -> str:
    txt = PHRASES_RU.replace('title.users', len_users=len(users_info))
    for user in users_info:
        emoji = get_query_count_emoji(user.query_count)
        admin_flag = ' 👑 |' if user.is_admin else ''
        banned = '💀 ' if user.is_banned else ''
        username = f"@{user.username}" if user.username else '🐸'

        txt += (
            f'<b>{username}</b> {banned}| <i>{user.user_id}</i> |{admin_flag} '
            f'{emoji} {user.query_count} | {user.registration_date.strftime("%d.%m.%Y")}\n'
        )
    return txt


def format_queries_text(
        queries: List[QueryModel],
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        header_template: str = PHRASES_RU.title.user_query,
        line_template: str = PHRASES_RU.template.user_query,
        show_username: bool = False
) -> str:
    """
    Форматирует список запросов в текстовое сообщение.

    Args:
        queries: Список объектов QueryModel
        username: Имя пользователя (если есть)
        user_id: ID пользователя (если username отсутствует)
        header_template: Шаблон заголовка с {username} placeholder
        line_template: Шаблон строки запроса с {time} и {query} placeholders
        show_username: Показывать ли имя пользователя в каждой строке

    Returns:
        Отформатированная строка с историей запросов
    """
    username_display = f"@{username}" if username else (str(user_id) if user_id else "❓")
    txt = header_template.format(username=username_display)

    for query in queries:
        query_time = query.query_date.strftime("%d.%m.%Y %H:%M:%S") if query.query_date else '❓'
        user_query = clear_string(query.query_text).replace("\n", "\t")
        line_data = {
            'time': query_time,
            'query': user_query,
            'username': f"@{query.user.username}" if show_username and query.user and query.user.username else ""
        }
        line = line_template.format(**line_data)
        txt += line

    return txt
