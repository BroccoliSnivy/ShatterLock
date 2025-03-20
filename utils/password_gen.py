import random
    
def generate_password():
    letters = list("abcdefghijklmnopqrstuvwxyz")
    letters_but_uppercase = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    digits = list("0123456789")
    punctuation = list("@#$%&*")

    all_characters = letters + letters_but_uppercase + digits + punctuation

    length = 16
    password = ''.join(random.choice(all_characters) for _ in range(length))

    return password