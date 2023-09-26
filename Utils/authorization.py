from flask import redirect, url_for

LEVEL_3 = ["SU"]
LEVEL_2 = ["SU", "LIB_MNAG"]
LEVEL_1 = ["SU", "LIB_MNAG", "LIB"]
LEVEL_0 = ["SU", "LIB_MNAG", "LIB", "LIB_AUX"]


def authorization_required(level, level_required, error):
    def wrapper_1(func):
        def wrapper_2(*args, **kwargs):
            if level['user_rol'] in level_required:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('access_not_authorized'))

        return wrapper_2

    return wrapper_1

