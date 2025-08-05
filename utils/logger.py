import logging


# Логи, отладка, дебаг
def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    )
