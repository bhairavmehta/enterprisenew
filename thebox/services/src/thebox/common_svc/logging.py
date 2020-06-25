import logging

SERVICE_LOGGER_NAME = "service_logger"


def setup_service_logger(verbose=False) -> logging.Logger:
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    # HACK:
    #   for now this is just a console print logger
    #   before we implement full on logger that can
    #   log to difference source for debugging

    logger = logging.getLogger(SERVICE_LOGGER_NAME)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if not len(logger.handlers):
        print("Setup_service_logger: adding console handler for logging ...")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def acquire_service_logger() -> logging.Logger:
    return logging.getLogger(SERVICE_LOGGER_NAME)


def log_dump_truncate(o, maxlen=256):
    s = o if isinstance(o, str) else str(o)
    if len(s) <= maxlen:
        return s
    n_2 = int(maxlen) // 2 - 3
    n_1 = maxlen - n_2 - 3
    return '{0}...{1}'.format(s[:n_1], s[-n_2:])