import asyncio
import logging
import uuid

from data.confluence.api.session import SessionWrapper, ClientSessionExt


class TooManyTriesException(Exception):
    pass


TRANSACTION_RETRIES = 3

TRANSACTION_RETRIES_DELAY_SECS = 3


def configure(transaction_retries_max: int, transaction_retries_delay_secs: int):
    global TRANSACTION_RETRIES
    global TRANSACTION_RETRIES_DELAY_SECS
    TRANSACTION_RETRIES = transaction_retries_max
    TRANSACTION_RETRIES_DELAY_SECS = transaction_retries_delay_secs


def transaction():
    global TRANSACTION_RETRIES
    global TRANSACTION_RETRIES_DELAY_SECS
    def func_wrapper(f):
        async def wrapper(*args, **kwargs):
            transaction_id = str(uuid.uuid4())
            for retries in range(TRANSACTION_RETRIES):
                # noinspection PyBroadException
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    logging.warning('[%s] transaction error:', transaction_id)
                    logging.exception(e)
                logging.warning('[%s] transaction retries: %d', transaction_id, retries + 1)
                await asyncio.sleep(TRANSACTION_RETRIES_DELAY_SECS)
            raise TooManyTriesException('[{}]'.format(transaction_id))

        return wrapper

    return func_wrapper


class ApiBase:
    __session: SessionWrapper

    __config: dict

    def __init__(self, config: dict, session: SessionWrapper):
        self.__config = config
        self.__session = session

    @property
    def url(self) -> str:
        return self.__config['url']

    @property
    def is_cloud(self) -> bool:
        return self.__config['cloud'] == 1
    @property
    def session(self) -> ClientSessionExt:
        return self.__session.current

    async def release(self):
        if self.__session is not None:
            await self.__session.release()
