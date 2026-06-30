from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(user):
    # Hash the password
    user.password = password_hash.hash(user.password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)
