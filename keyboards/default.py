from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# кнопки выбора купить/посмотреть аккаунт
main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить доступ", callback_data="buy_access")],
        [InlineKeyboardButton(text="📄 Мой аккаунт", callback_data="my_account")],
        [InlineKeyboardButton(text="🛠️ Тех. поддержка", callback_data="support")]
    ],
    resize_keyboard=True
)

# кнопки выбора времени подписки
choice_time_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1 день 50₽", callback_data="1_day")],
        [InlineKeyboardButton(text="3 дня 75₽", callback_data="3_day")],
        [InlineKeyboardButton(text="7 дней 100₽", callback_data="7_day")],
        [InlineKeyboardButton(text="1 месяц 250₽", callback_data="1_month")],
        [InlineKeyboardButton(text="3 месяца 600₽", callback_data="3_month")],
        [InlineKeyboardButton(text="1 год 2000₽", callback_data="1_year")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="to_main_menu")]
    ],
    resize_keyboard=True
)

# кнопки оплаты
payment_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить через СБП (QR-код)", callback_data="pay_sbp")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="to_main_menu")]
    ],
    resize_keyboard=True
)

# кнопка подтверждения оплаты
confirm_or_deny_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="pay_paid")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="to_main_menu")]
    ],
    resize_keyboard=True
)

# просто кнопка в главное меню
back_to_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="to_main_menu")]
    ],
    resize_keyboard=True
)

# кнопки для админов
admin_action_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_user_button"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_user_button"),
        ],
        [
            InlineKeyboardButton(text="💬 Связаться", callback_data="call_user_button")
        ]
    ]
)

# кнопка назад универсальная (чуть позже доработаю)
# def back_button(callback_data: str) -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data)]
#         ]
#     )
