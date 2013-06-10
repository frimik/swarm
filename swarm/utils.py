import threading


def spawn(function, *args, **kwargs):
    thread = threading.Thread(target=function, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


def spawn_later(seconds, function, *args, **kwargs):
    thread = threading.Timer(seconds, function, args, kwargs)
    thread.daemon = True
    thread.start()
    return thread

