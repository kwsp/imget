import logging

logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)

logger.debug("debug")
logger.info("info")
logger.warning("warning")
logger.error("error")
logger.critical("critical")
