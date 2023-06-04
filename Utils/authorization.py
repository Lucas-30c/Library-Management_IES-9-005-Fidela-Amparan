# Roles serán
from flask import redirect, url_for

LEVEL_2 = ["SU"]
LEVEL_1 = ["SU", "LIB"]
LEVEL_0 = ["SU", "LIB", "LIB_AUX"]


def authorization_required(level, level_required, error):
    def wrapper_1(func):
        def wrapper_2(*args, **kwargs):
            if level['user_rol'] in level_required:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('access_not_authorized'))

        return wrapper_2

    return wrapper_1



# @authorization_required(level="LIB", level_required=LEVEL_2, error_url="Errorazo!!")
# def testing_decorador():
#     print("Hola Mundo!!")
