from sqlalchemy.orm import sessionmaker

from db.create_db import engine, Payment

SessionLocal = sessionmaker(bind=engine)


def add_payment(tg_user_id: int, username: str, payment_method: str, status: str, duration: int):
    """Добавление юзера в базу данных"""
    session = SessionLocal()
    try:
        new_payment = Payment(
            tg_user_id=tg_user_id,
            username=username,
            payment_method=payment_method,
            status=status,
            duration=duration,
        )
        session.add(new_payment)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()
