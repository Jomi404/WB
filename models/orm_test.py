import re
from datetime import datetime
from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import models
from keyboards import MainMenuCbData1
from logger import CustomFormatter
import logging
import asyncio

import math
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from engine import create_db
from orm_query import orm_get_banner

from paginator import Paginator

############################ Акции ######################################


DB_LITE = "sqlite+aiosqlite:///W:/Чист/Monitoring/data/database"


async def orm_get_promos(session: AsyncSession):
    query = select(models.Promo)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_promo(session: AsyncSession, promo: dict):
    obj = models.Promo(promo_name=promo['promo_name'],
                       promo_description=promo['promo_description'],
                       promo_url=promo['promo_url'],
                       )
    session.add(obj)
    await session.commit()


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


def get_promos_btns(
        *,
        level: int,
        page: int,
        pagination_btns: dict,
        promo_id: int,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=level - 1, menu_name='menu'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


async def orm_add_doctor(session: AsyncSession, doctor: dict):
    obj = models.Doctors(doctor_id=doctor['doctor_id'],
                         fio_doctor=doctor['fio_doctor'],
                         direction=doctor['direction'],
                         image=doctor.get('image', 'W:\\Чист\\Monitoring\\data\\image\\expert.webp')
                         )
    session.add(obj)
    await session.commit()


async def orm_add_banner_description(session: AsyncSession, data: dict):
    # Добавляем новый или изменяем существующий по именам
    # пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(models.Banners)
    result = await session.execute(query)
    session.add_all([models.Banners(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def get_fio_by_user_id(session: AsyncSession, user_id: int) -> str:
    query = select(models.Crm.full_name).where(models.Crm.user_id == user_id)
    result = await session.execute(query)
    user_fio = result.scalar_one_or_none()
    return user_fio


async def orm_add_reception_history(session: AsyncSession, reception_history: dict):
    obj = models.ReceptionHistory(fio_client=reception_history['fio_client'],
                                  fio_doctor=reception_history['fio_doctor'],
                                  spec_doctor=reception_history['spec_doctor'],
                                  date=reception_history['date'],
                                  diagnosis=reception_history['diagnosis']
                                  )
    session.add(obj)
    await session.commit()


async def orm_get_receptions_history(session: AsyncSession, user_id: int):
    fio_client = await get_fio_by_user_id(session=session, user_id=user_id)
    query = select(models.ReceptionHistory.fio_doctor).where(models.ReceptionHistory.fio_client == fio_client)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_doctors(session: AsyncSession):
    query = select(models.Doctors)
    result = await session.execute(query)
    return result.scalars().all()


'''    data = {
            "fio_client": "Амошенко Александр Иванович",
            "fio_doctor": "Петр Петр Петр",
            "spec_doctor": "Кардиолог",
            "date": "2024-07-10 14:30:00",
            "diagnosis": "Тест"
        }'''

'''if isinstance(data.get('date'), str):
        data['date'] = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')'''


async def orm_get_reception_history_info(session: AsyncSession, user_id: int):
    fio_client = await get_fio_by_user_id(session=session, user_id=user_id)
    query = select(models.ReceptionHistory.fio_doctor, models.ReceptionHistory.date,
                   models.ReceptionHistory.diagnosis).where(models.ReceptionHistory.fio_client == fio_client)
    result = await session.execute(query)
    return result.fetchall()


class MainMenuCbData12(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    page: int = 1
    promo_id: int | None = None
    doctor_id: int | None = None


class Paginator2:
    def __init__(self, array: list | tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        # math.ceil - округление в большую сторону до целого числа
        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_items = self.__get_slice()
        return page_items


def test_button(
        *,
        level: int,
        page: int,
        pagination_btns: dict,
        page_button: list,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()
    for page_info in page_button:
        keyboard.button(text=page_info, callback_data='test')

    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


async def test_history_menu(session, level, menu_name, user_id, page):
    banner = await orm_get_banner(session, 'reception_history')

    data = await orm_get_reception_history_info(session=session, user_id=user_id)
    fio_doctors = [data[i][0] for i in range(len(data))]  # ['','','']

    paginator = Paginator(fio_doctors, page=page, per_page=2)

    page_button_list = paginator.get_page()

    pagination_btns = pages(paginator)

    image = InputMediaPhoto(
        media=banner.image,
        caption="sdsd"

    )

    pagination_btns = pages(paginator)

    kbds = test_button(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        page_button=page_button_list

    )

    return image, kbds


async def get_id_doctor_by_fio(session: AsyncSession, fio_doctor: str) -> int:
    query = select(models.Doctors.id).where(models.Doctors.fio_doctor == fio_doctor)
    result = await session.execute(query)
    doctor_id = result.scalar_one_or_none()
    return doctor_id


async def orm_add_doctor_test(session: AsyncSession, doctor: dict):
    obj = models.Doctors(doctor_id=doctor['doctor_id'],
                         fio_doctor=doctor['fio_doctor'],
                         direction=doctor['direction'],
                         image=doctor.get('image', 'W:\\Чист\\Monitoring\\data\\image\\expert.webp')
                         )
    session.add(obj)
    await session.commit()


# получаем ФИО врача и его id
async def get_doctors_fio_id(session: AsyncSession, user_id: int):
    query = (
        select(models.Doctors.fio_doctor, models.Doctors.id).join(models.ReceptionHistory,
                                                                  models.ReceptionHistory.fio_doctor == models.Doctors.fio_doctor).join(
            models.Crm,
            models.Crm.full_name == models.ReceptionHistory.fio_client).filter(models.Crm.user_id == user_id)
    )
    result = await session.execute(query)

    doctors = result.fetchall()
    return doctors


def find_id(name, list2):
    for item in list2:
        if name in item:
            return item[name]


def get_receptions_history_doctor(
        *,
        level: int,
        page: int,
        pagination_btns: dict,
        data_for_button: list,
        page_button_list: list,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()
    new_data = []
    for name in page_button_list:
        id_ = find_id(name, data_for_button)
        new_data.append({'text': name, 'id': id_})

    print(data_for_button)
    print(page_button_list)
    for page_info in new_data:
        print(page_info['text'])
        print(page_info['id'])
        keyboard.button(text=page_info['text'],
                        callback_data=MainMenuCbData1(level=8, menu_name='visit_dates', doctor_id=page_info['id']))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    # keyboard.adjust(*sizes)


async def reception_history_menu(session, level, user_id, page):
    # получаем картинку
    banner = await orm_get_banner(session, 'reception_history')

    # нужно получить фамилии врачей у кого был пользователь и их id
    doctors_fios_ids = await get_doctors_fio_id(session=session, user_id=user_id)
    data_for_button = [{fio_doctor: doctor_id} for fio_doctor, doctor_id in doctors_fios_ids]
    fio_doctors = [doctors_fios_ids[i][0] for i in range(len(doctors_fios_ids))]

    paginator = Paginator(fio_doctors, page=page, per_page=4)
    page_button_list = paginator.get_page()
    print(page_button_list)
    print(data_for_button)
    image = InputMediaPhoto(
        media=banner.image,
        caption='Список врачей:'

    )

    pagination_btns = pages(paginator)
    get_receptions_history_doctor(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        page_button_list=page_button_list,
        data_for_button=data_for_button,
    )


'''kbds = get_receptions_history_doctor(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        page_button=page_button_list,
        data_for_button=data_for_button
    )

    return image, kbds'''


async def get_dates_by_user_id(session: AsyncSession, user_id: int, doctor_id: int):
    query = select(models.ReceptionHistory.date).join(models.Doctors,
                                                      models.ReceptionHistory.fio_doctor == models.Doctors.fio_doctor).join(
        models.Crm, models.ReceptionHistory.fio_client == models.Crm.full_name).filter(
        models.Doctors.doctor_id == doctor_id,
        models.Crm.user_id == user_id)

    result = await session.execute(query)

    dates = result.fetchall()
    return dates


async def orm_add_reception_history1(session: AsyncSession, reception_history: dict):
    obj = models.ReceptionHistory(fio_client=reception_history['fio_client'],
                                  fio_doctor=reception_history['fio_doctor'],
                                  spec_doctor=reception_history['spec_doctor'],
                                  date=reception_history['date'],
                                  diagnosis=reception_history['diagnosis']
                                  )
    session.add(obj)
    await session.commit()


async def orm_add_banner_description1(session: AsyncSession, data: dict):
    # Добавляем новый или изменяем существующий по именам
    # пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(models.Banners)
    result = await session.execute(query)

    session.add_all([models.Banners(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def get_dig_by_user_id(session: AsyncSession, user_id: int, doctor_id: int, date: str):
    date_object = datetime.strptime(date, "%d-%m-%Y")
    query = select(models.ReceptionHistory.diagnosis).join(models.Doctors,
                                                           models.ReceptionHistory.fio_doctor == models.Doctors.fio_doctor).join(
        models.Crm, models.ReceptionHistory.fio_client == models.Crm.full_name).filter(
        models.Doctors.doctor_id == doctor_id,
        models.Crm.user_id == user_id, models.ReceptionHistory.date == date_object)

    result = await session.execute(query)

    diagnosis = result.scalar_one_or_none()
    return diagnosis


async def insert_specialty(session, name_specialty):
    new_specialty = models.Specialties(name_specialty=name_specialty)
    session.add(new_specialty)
    await session.commit()


async def get_name_specialty_id(session: AsyncSession):
    query = select(models.Specialties.name_specialty, models.Specialties.id)
    result = await session.execute(query)

    name_specialty_id = result.fetchall()

    return name_specialty_id


async def insert_analysis_history(session, data: dict):
    new_analysis_history = models.AnalysisHistory(
        specialty_id=data['specialty_id'],
        user_id=data['user_id'],
        fio_client=data['fio_client'],
        analysis_file=data['analysis_file']
    )
    session.add(new_analysis_history)
    await session.commit()


async def insert_admin(session, user_id: int):
    new_admin = models.Admins(
        user_id=user_id,
    )
    session.add(new_admin)
    await session.commit()


async def get_analysis_file(session: AsyncSession, user_id: int, specialty_id: int):
    query = select(models.AnalysisHistory.analysis_file).filter(models.AnalysisHistory.user_id == user_id,
                                                                models.AnalysisHistory.specialty_id == specialty_id)

    result = await session.execute(query)

    result_file = result.scalar_one_or_none()

    return result_file


async def isAdmins(session: AsyncSession, user_id: int):
    query = select(models.Admins.user_id).filter(models.Admins.user_id == user_id)

    result = await session.execute(query)

    isAdmins = result.scalar_one_or_none()

    return False if isAdmins is None else True


async def insert_text_hi(session, text: str):
    new_admin = models.TextHi(
        text=text,
    )
    session.add(new_admin)
    await session.commit()


async def update_text_hi(session, new_text: str):
    stmt = update(models.TextHi).where(models.TextHi.id == 1).values(text=new_text)
    await session.execute(stmt)
    await session.commit()


async def get_text_hi(session, text_id: int) -> str:
    stmt = select(models.TextHi).where(models.TextHi.id == text_id)
    result = await session.execute(stmt)

    string = result.scalar_one_or_none()

    return None if string is None else string.text


async def orm_delete_promo(session: AsyncSession, promo_name: str):
    query = delete(models.Promo).where(models.Promo.promo_name == promo_name)
    test = await session.execute(query)
    await session.commit()

async def main():
    await create_db()
    engine = create_async_engine(DB_LITE, echo=True)
    session_marker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    level = 8
    menu_name = 'reception_history'
    page = 1

    data = {
        "edit_promo_menu": 'Редактирование акций:',
    }

    if isinstance(data.get('date'), str):
        data['date'] = datetime.strptime(data['date'], '%d-%m-%Y')
    async with session_marker() as session:
        pass
        #test = await orm_get_users(session)


if __name__ == "__main__":
    asyncio.run(main())
