import logging


class Logger:
    def __init__(self, level=logging.DEBUG):
        self._logger = logging.getLogger("imget")
        logging.basicConfig()
        self._logger.setLevel(level=level)

    def info(self, msg: str):
        self._logger.info(msg)

    def debug(self, msg: str):
        self._logger.debug(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def critical(self, msg: str):
        self._logger.critical(msg)


def init_logger(level=logging.DEBUG):
    global logger
    logger = Logger(level)


def get_logger():
    return logger


if __name__ == "__main__":
    init_logger(logging.DEBUG)
    get_logger().info("info")
    get_logger().debug("debug")
    get_logger().warning("warning")
    get_logger().error("error")
    get_logger().critical("critical")
