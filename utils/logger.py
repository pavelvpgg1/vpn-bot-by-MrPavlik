import logging


def setup_logger():
    """Логи, отладка, дебаг"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    )
