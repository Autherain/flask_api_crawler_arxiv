import logging


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - [%(process)d:%(thread)d] - %(filename)s:%(funcName)s() - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
