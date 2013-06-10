import threading

Event = threading.Event


def spawn(function, *args, **kwargs):
    """Spawns a daemonized thread.`"""
    thread = threading.Thread(target=function, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


def spawn_later(seconds, function, *args, **kwargs):
    """Spawns a daemonized thread after `seconds.`"""
    thread = threading.Timer(seconds, function, args, kwargs)
    thread.daemon = True
    thread.start()
    return thread