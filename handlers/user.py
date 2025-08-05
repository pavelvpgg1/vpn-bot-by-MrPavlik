import datetime

import pytz
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.orm import sessionmaker

from db.add import add_payment
from db.create_db import Payment, engine
from handlers.api_3xui import create_client_for_user, generate_vpn_link
from keyboards.default import main_keyboard, choice_time_keyboard, payment_keyboard, confirm_or_deny_keyboard

SUBSCRIPTION_TEXTS = {
    "1_day": ["1 день", 1],
    "3_day": ["3 дня", 3],
    "7_day": ["7 дней", 7],
    "1_month": ["1 месяц", 30],
    "3_month": ["3 месяца", 90],
    "1_year": ["1 год", 365]
}
PAYMENT_METHOD = ""
DURATION = 0
router = Router()
SessionLocal = sessionmaker(bind=engine)


# Взаимодействие с юзером
@router.message(Command("start")) # команда /start -> Выбор тарифа/Инфо об аккаунте
async def start_handler(message: Message):
    await message.answer("Привет! Выбери тариф, чтобы купить VPN-доступ.", reply_markup=main_keyboard)


@router.callback_query(F.data == "to_main_menu") # Выбор тарифа/Инфо об аккаунте
async def handle_back_to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Главное меню", reply_markup=main_keyboard)


@router.callback_query(F.data == "buy_access") # Выбор продолжительности подписки
async def handle_buy_access(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Выбери продолжительность подписки:", reply_markup=choice_time_keyboard)


@router.callback_query(F.data.in_(SUBSCRIPTION_TEXTS.keys())) # Выбор способа оплаты
async def handle_subscription_choice(callback: CallbackQuery):
    duration = SUBSCRIPTION_TEXTS[callback.data][0]
    await callback.answer()
    await callback.message.answer(f"Вы выбрали продолжительность подписки: `{duration}`", parse_mode="Markdown")
    await callback.message.answer("Выберите способ оплаты:", reply_markup=payment_keyboard)
    global DURATION
    DURATION = SUBSCRIPTION_TEXTS[callback.data][1]


@router.callback_query(F.data == "pay_sbp") # Оплата по СБП
async def pay_sbp_handler(callback: CallbackQuery):
    await callback.answer()
    photo = FSInputFile("images/qr_sbp.png")
    await callback.message.answer_photo(
        photo=photo,
        caption=(
            "💸 Оплатите через СБП по QR-коду."
        )
    )
    await callback.message.answer(
        f"❗❗❗В комментарии к оплате укажите свой тг id \n🆔 Telegram ID: `{callback.from_user.id}`",
        reply_markup=confirm_or_deny_keyboard,
        parse_mode="Markdown"
    )
    global PAYMENT_METHOD
    PAYMENT_METHOD = "оплата по СБП"


@router.callback_query(F.data == "pay_paid") # Подтверждение
async def pay_paid_handler(callback: CallbackQuery):
    tg_user_id = callback.from_user.id
    username = callback.from_user.username
    payment_method = PAYMENT_METHOD
    status = "pending"
    duration = DURATION

    success = add_payment(tg_user_id, username, payment_method, status, duration)
    if success:
        await callback.message.answer("💾Ваш запрос принят на рассмотрение, в течение часа будет готов ваш доступ к VPN")
    else:
        await callback.message.answer("❗Что-то пошло не так! Пожалуйста, обратитесь к администрартору (@pavelvpgg1)")


# Аккаунт пользователя
@router.callback_query(F.data == "my_account") # Инфо об аккаунте
async def handle_my_account(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Твой аккаунт:")


# Админка
@router.message(Command("approve")) # Подтвердить запрос
async def approve_payment(message: Message):
    if message.from_user.id not in [2100039698]:  # тг айди админов
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
        create_client_for_user(tg_user_id=user_id, duration_days=duration)
        vpn_link = generate_vpn_link(f"{user_id}@MrPavlik.ru")

        # Отправить юзеру VPN-инструкцию
        await message.bot.send_message(
            chat_id=user_id,
            text=(
                f"🔐 Оплата подтверждена! Вот ваша ссылка на VPN: `{vpn_link}`\n\n"
                "Инструкция по подключению: ..."
            ),
            parse_mode="Markdown"
        )

        await message.answer(f"✅ Доступ выдан пользователю {user_id}")
    except Exception as e:
        await message.answer("❗ Ошибка при выдаче доступа! Пожалуйста, обратитесь к администрартору (@pavelvpgg1)")
        print(f"[approve error] {e}")
        session.rollback()
    finally:
        session.close()
