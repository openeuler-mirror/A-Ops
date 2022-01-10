import threading


class Singleton(type):
    _instance_lock = threading.Lock()

    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super(Singleton, cls).__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            with Singleton._instance_lock:
                if cls._instance is None:
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
