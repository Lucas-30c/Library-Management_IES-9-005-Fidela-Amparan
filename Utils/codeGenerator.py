import random
import string


def generate_confirmation_code():
    letters = random.choice(string.ascii_uppercase)
    numbers = ''.join(random.choice(string.digits) for i in range(4))
    code = letters + numbers
    return code
