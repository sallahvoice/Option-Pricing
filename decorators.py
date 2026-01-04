def timing(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {(start-end)*1000.:4f} ms to excute")
    
    return decorator

def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
    if cls not in instances:
        instances[cls] = cls(*args, **kwargs)

        return instances[cls]
    return wrapper

class RetryException(Exception):
    pass

def retry(max_attempts: int=4, delay: float=1.0, backoff_factor: float=2.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwrags)
                except Exception as e:
                    last_exception = (
                        f"{func.__name__} failed after attempt {attempt} due to: {e}"
                    )
                    if attempt < max_attempts:
                        current_delay *= backoff_factor
                        time.sleep(current_delay)
                        
            raise RetryException from None
        return wrapper
    return decorator
            