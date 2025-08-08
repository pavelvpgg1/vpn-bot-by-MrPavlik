from aiogram.fsm.state import State, StatesGroup

class PaymentState(StatesGroup):
    """Хранилище данных в определенном чате с юзером"""
    choosing_duration = State()
    choosing_payment_method = State()
    awaiting_confirmation = State()
