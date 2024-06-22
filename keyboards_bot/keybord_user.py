from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_btns(link: str, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Перейти к покупкам', web_app=WebAppInfo(url=link))
    keyboard.button(text='О сервисе', callback_data='about')
    keyboard.button(text='Инструкция размещения', callback_data='place_instruct')
    return keyboard.adjust(*sizes).as_markup()


def get_about_btns(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='О сервисе', url='https://telegra.ph/O-servise-06-21')
    keyboard.button(text='Инструкция размещения', url='https://telegra.ph/Instrukciya-razmeshcheniya-06-21')
    keyboard.button(text="Назад", callback_data='menu')
    return keyboard.adjust(*sizes).as_markup()


def get_place_instruct_info_btns(link: str, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Разместить товар', web_app=WebAppInfo(url=link))
    keyboard.button(text="Назад", callback_data='menu')
    return keyboard.adjust(*sizes).as_markup()
