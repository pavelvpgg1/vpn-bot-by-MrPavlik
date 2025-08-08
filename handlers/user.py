import datetime

import pytz
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.orm import sessionmaker

from db.add import add_payment
from db.create_db import Payment, engine
from handlers.api_3xui import create_client_for_user, generate_vpn_link
from keyboards.default import (main_keyboard,
                               choice_time_keyboard,
                               payment_keyboard,
                               confirm_or_deny_keyboard,
                               back_to_main_menu_keyboard)
from utils.states import PaymentState

SUBSCRIPTION_TEXTS = {
    "1_day": ["1 день", 1],
    "3_day": ["3 дня", 3],
    "7_day": ["7 дней", 7],
    "1_month": ["1 месяц", 30],
    "3_month": ["3 месяца", 90],
    "1_year": ["1 год", 365]
}
ADMIN_ID = {
    "@pavelvpgg1": 2100039698,
    "@Orin286": 1171128013,
    "@DdOaNrYk_0": 1894484454
}

router = Router()
SessionLocal = sessionmaker(bind=engine)


# Взаимодействие с юзером
@router.message(Command("start"))
async def start_handler(message: Message):
    """команда /start -> Выбор тарифа/Инфо об аккаунте"""
    await message.answer(
        "Привет! Выбери тариф, чтобы купить VPN-доступ.",
        reply_markup=main_keyboard
    )


@router.callback_query(F.data == "to_main_menu")
async def handle_back_to_main(callback: CallbackQuery):
    """Выбор тарифа/Инфо об аккаунте"""
    await callback.message.answer(
        "Главное меню",
        reply_markup=main_keyboard
    )


@router.callback_query(F.data == "buy_access")
async def handle_buy_access(callback: CallbackQuery):
    """Выбор продолжительности подписки"""
    await callback.message.answer(
        "Выбери продолжительность подписки:",
        reply_markup=choice_time_keyboard
    )


@router.callback_query(F.data == "support")
async def handle_support(callback: CallbackQuery):
    """Обращение к технической поддержке"""
    await callback.answer()
    await callback.message.answer(
        "👨‍💻 По всем вопросам обращайтесь к администратору: @pavelvpgg1",
        reply_markup=back_to_main_menu_keyboard
    )


@router.callback_query(F.data.in_(SUBSCRIPTION_TEXTS.keys()))
async def handle_subscription_choice(callback: CallbackQuery, state: FSMContext):
    """Выбор способа оплаты"""
    duration_label, duration_days = SUBSCRIPTION_TEXTS[callback.data]
    await callback.message.answer(
        f"⌛ Вы выбрали продолжительность подписки: `{duration_label}`",
        parse_mode="Markdown"
    )
    await callback.message.answer(
        "🔀 Выберите способ оплаты:",
        reply_markup=payment_keyboard
    )

    await state.update_data(duration=duration_days)
    await state.set_state(PaymentState.choosing_payment_method)


@router.callback_query(F.data == "pay_sbp")
async def pay_sbp_handler(callback: CallbackQuery, state: FSMContext):
    """Оплата по СБП"""
    photo = FSInputFile("images/qr_sbp.png")
    await callback.message.answer_photo(
        photo=photo,
        caption=(
            "💸 Оплатите через СБП по QR-коду."
        )
    )
    await callback.message.answer(
        f"❗❗❗В комментарии к оплате укажите свой тг id \n🆔 Ваш telegram ID: `{callback.from_user.id}`",
        reply_markup=confirm_or_deny_keyboard,
        parse_mode="Markdown"
    )
    await state.update_data(payment_method="СБП")
    await state.set_state(PaymentState.awaiting_confirmation)


@router.callback_query(F.data == "pay_paid")
async def pay_paid_handler(callback: CallbackQuery, state: FSMContext):
    """Подтверждение от пользователя, что он оплатил"""
    tg_user_id = callback.from_user.id
    username = callback.from_user.username
    data = await state.get_data()
    duration = data.get("duration")
    payment_method = data.get("payment_method")
    status = "pending"

    success = add_payment(tg_user_id, username, payment_method, status, duration)
    if success:
        await callback.message.answer(
            "💾 Ваш запрос принят на рассмотрение, в течение часа будет готов ваш доступ к VPN",
            reply_markup=back_to_main_menu_keyboard
        )
        await state.clear()
    else:
        await callback.message.answer(
            "❗ Что-то пошло не так! Пожалуйста, обратитесь к администрартору (@pavelvpgg1)"
        )


# Аккаунт пользователя
@router.callback_query(F.data == "my_account")
async def handle_my_account(callback: CallbackQuery):
    """Инфо об аккаунте пользователя"""
    session = SessionLocal()
    try:
        payment = session.query(Payment).filter_by(tg_user_id=int(callback.from_user.id)).first()

        if not payment:
            await callback.message.answer("❌ Вы еще не покупали доступ")
            return

        # Данные пользователя
        payment_method = payment.payment_method
        status = payment.status
        if status == "approved":
            active_until = (datetime.datetime.now(pytz.timezone("Asia/Yekaterinburg")) + datetime.timedelta(
                days=payment.duration)).strftime("%d.%m.%Y")
            days_left = ((payment.created_at + datetime.timedelta(days=payment.duration)) - payment.created_at).days
            approved_by = [key for key, value in ADMIN_ID.items() if value == payment.approved_by][0]
            await callback.message.answer(
                text=("⚙️ Ваш аккаунт:\n"
                      f"📛 Имя: `{callback.from_user.first_name}`\n"
                      f"⌛ Подписка активна до: `{active_until}`\n"
                      f"⏳ До конца подписки: {days_left} дней\n"
                      f"💸 Оплата была произведена при помощи: `{payment_method}`\n"
                      f"✨ Статус вашей оплаты: `{status}`\n"
                      f"✅ Ваш запрос подтвердил админ: `{approved_by}`\n"),
                parse_mode="Markdown", reply_markup=back_to_main_menu_keyboard
            )
        elif status == "pending":
            await callback.message.answer(
                text=("⚙️ Ваш аккаунт:\n"
                      f"📛 Имя: `{callback.from_user.first_name}`\n"
                      f"💸 Оплата была произведена при помощи: `{payment_method}`\n"
                      f"🕔 Статус вашей оплаты: `{status}`\n"
                      "❗Ваш запрос пока что не подтвержден\n"),
                parse_mode="Markdown", reply_markup=back_to_main_menu_keyboard
            )
        elif status == "rejected":
            await callback.message.answer(
                text=("⚙️ Ваш аккаунт:\n"
                      f"📛 Имя: `{callback.from_user.first_name}`\n"
                      f"❌ Статус вашей оплаты: `{status}`\n"
                      "❗Ваш запрос был отклонен. Если эта была ошибка, пожалуйста, свяжитесь с тех.поддержкой\n"),
                parse_mode="Markdown", reply_markup=back_to_main_menu_keyboard
            )

    except Exception as e:
        await callback.message.answer(
            "❗ Ошибка при попытке просмотра аккаунта! Пожалуйста, обратитесь к тех.поддержке.",
            reply_markup=back_to_main_menu_keyboard
        )
        print(f"[account error] {e}")
        session.rollback()
    finally:
        session.close()


# Админка
@router.message(Command("approve"))
async def approve_payment(message: Message):
    """Подтвердить запрос на выдачу ВПН ссылки"""
    if message.from_user.id not in list(ADMIN_ID.values()):  # тг айди админов
        return

    try:
        _, user_id_str = message.text.split()
        user_id = int(user_id_str)
    except Exception:
        await message.answer("❌ Формат команды: /approve <user_id>")
        return

    # Создаём сессию с базой
    session = SessionLocal()
    try:
        payment = session.query(Payment).filter_by(tg_user_id=user_id).first()

        if not payment or payment.status != "pending":
            await message.answer("❌ Пользователь не найден или уже подтвержден.")
            return

        # Обновить статус
        duration = payment.duration
        payment.status = "approved"
        payment.approved_by = message.from_user.id
        payment.confirmed_at = datetime.datetime.now(pytz.timezone("Etc/GMT-5"))
        session.commit()
        await create_client_for_user(tg_user_id=user_id, duration_days=duration)
        vpn_link = await generate_vpn_link(f"{user_id}@MrPavlik.ru")

        # Отправить юзеру VPN-инструкцию
        await message.bot.send_message(
            chat_id=user_id,
            text=(
                f"🔐 Оплата подтверждена! Вот ваша ссылка на VPN: `{vpn_link}`\n\n"
                "❗️❗️❗️Туториал по VPN'у❗️❗️❗️\n"
                "Android📱:\n"
                "1) Устанавливаем *v2rayNG* (ниже apk файл под названием `v2rayNG_1.9.30_APKPure.apk`)\n"
                "2) Заходим -> Нажимаем на \"*+*\" -> *Импорт из буфера обмена* -> должен появиться новый профиль -> нажимаем на профиль -> в правом нижнем углу нажимаем кнопку \"*Пуск*\"\n\n"
                "IPhone📱:\n"
                "1) Устанавливаем *V2RayTun* с AppStore ([ссылка на приложение](https://apps.apple.com/kz/app/v2raytun/id6476628951))\n"
                "2) Заходим в приложение\n"
                "3) В правом верхнем углу нажимаем \"*+*\" -> \"*Добавить из буфера обмена*\" (Скопируйте ссылку, которую выдал бот) -> должен появиться новый профиль\n"
                "4) Нажимаем *кнопку запуска* посередине\n\n"
                "Windows🖥️:\n"
                "1) Устанавливаем архив с *Nekobox* (ниже zip архив под названием `nekoray-4.0.1-2024-12-12-windows64.zip`)\n"
                "2) Распаковываем архив\n"
                "3) Запускаем \"*nekobox.exe*\"\n"
                "4) Нажимаем кнопку \"*Сервер*\" -> \"*Добавить из буфера обмена*\" (Скопируйте ссылку, которую выдал бот) -> ставим галочку сверху на пункте \"*Режим TUN*\" -> Нажимаем *правую кнопку мыши* по появившемуся соединению -> Выбираем пункт \"*Запустить*\"\n\n"
                "Linux🖥️:\n"
                "1) Устанавливаем архив с *Nekobox* (ниже zip архив под названием `nekoray-4.0.1-2024012012-linux64.zip`)\n"
                "2) Распаковываем архив\n"
                "3) Запускаем \"*nekobox.exe*\"\n"
                "4) Нажимаем кнопку \"*Сервер*\" -> \"*Добавить из буфера обмена*\" (Скопируйте ссылку, которую выдал бот) -> ставим галочку сверху на пункте \"*Режим TUN*\" -> Нажимаем *правую кнопку мыши* по появившемуся соединению -> Выбираем пункт \"*Запустить*\"\n\n"
            ),
            parse_mode="Markdown"
        )

        # файл для Android
        v2ray_android = FSInputFile("files/v2rayNG_1.9.30_APKPure.apk")
        await message.bot.send_document(
            chat_id=user_id,
            document=v2ray_android,
            caption="📱 Приложение для Android"
        )

        # файл для Windows
        neko_windows = FSInputFile("files/nekoray-4.0.1-2024-12-12-windows64.zip")
        await message.bot.send_document(
            chat_id=user_id,
            document=neko_windows,
            caption="🖥️ Приложение для Windows"
        )

        # файл для Linux
        neko_linux = FSInputFile("files/nekoray-4.0.1-2024-12-12-linux64.zip")
        await message.bot.send_document(
            chat_id=user_id,
            document=neko_linux,
            caption="🖥️ Приложение для Linux")

        await message.answer(f"✅ Доступ выдан пользователю {user_id}")
    except Exception as e:
        await message.answer("❗ Ошибка при выдаче доступа!")
        print(f"[approve error] {e}")
        session.rollback()
    finally:
        session.close()


@router.message(Command("reject"))
async def reject_payment(message: Message):
    """Отклонить запрос на выдачу ВПН ссылки"""
    if message.from_user.id not in list(ADMIN_ID.values()):
        return

    try:
        _, user_id_str = message.text.split()
        user_id = int(user_id_str)
    except Exception:
        await message.answer("❌ Формат команды: /reject <user_id>")
        return

    session = SessionLocal()
    try:
        payment = session.query(Payment).filter_by(tg_user_id=user_id).first()

        if not payment or payment.status != "pending":
            await message.answer("❌ Пользователь не найден или уже подтвержден/отклонен.")
            return

        payment.status = "rejected"
        session.commit()

        await message.bot.send_message(
            chat_id=user_id,
            text="❌ Ваша заявка на VPN-доступ была отклонена. Пожалуйста, обратитесь к тех.поддержке.",
            reply_markup=back_to_main_menu_keyboard
        )

        await message.answer(f"🚫 Запрос пользователя {user_id} отклонен.")
    except Exception as e:
        await message.answer("❗ Ошибка при отклонении запроса!")
        print(f"[reject error] {e}")
        session.rollback()
    finally:
        session.close()

# дебаг
# @router.callback_query()
# async def debug_callback(callback: CallbackQuery):
#     print("[DEBUG] callback.data =", callback.data)
#     await callback.answer("⚠️ Необработанный callback.")
