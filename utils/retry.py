import logging
import time
from functools import wraps
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)

# List of transient errors that are safe to retry
TRANSIENT_ERRORS: Tuple[Type[Exception], ...] = (
    OperationalError,
    ConnectionError,
)

def retry_db_operation(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_backoff: bool = True
):
    """
    Decorator to retry database operations with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds
        exponential_backoff: Whether to use exponential backoff
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except TRANSIENT_ERRORS as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Database operation failed after {max_retries} retries: {str(e)}", exc_info=True)
                        raise
                    
                    # Calculate delay
                    if exponential_backoff:
                        delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    else:
                        delay = base_delay
                    
                    logger.warning(
                        f"Database transient error (attempt {retries}/{max_retries}), "
                        f"retrying in {delay:.1f}s: {str(e)}"
                    )
                    time.sleep(delay)
                except SQLAlchemyError as e:
                    logger.error(f"Non-transient database error, not retrying: {str(e)}", exc_info=True)
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in database operation: {str(e)}", exc_info=True)
                    raise
        return wrapper
    return decorator
