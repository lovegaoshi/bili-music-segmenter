import logging
import time

class MaxRetryReached(BaseException):
    pass

def retry(times: int, timeout: int, exceptions: tuple):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logging.warning(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt + 1, times)
                    )
                    attempt += 1
                    if attempt == times:
                        raise MaxRetryReached()
                    time.sleep(timeout)
            return func(*args, **kwargs)
        return newfn
    return decorator
