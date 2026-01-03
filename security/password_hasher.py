from argon2 import PasswordHasher as _Argon2Hasher
from argon2.exceptions import VerifyMismatchError


class PasswordHasher:

    def __init__(self):
        self._hasher = _Argon2Hasher(
            time_cost=2,
            memory_cost=102400,
            parallelism=8,
            hash_len=32,
            salt_len=16
        )

    def hash_password(self, plain_password: str) -> str:
        if not plain_password:
            raise ValueError("Password cannot be empty")

        return self._hasher.hash(plain_password)

    def verify_password(self, password_hash: str, plain_password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, plain_password)
        except VerifyMismatchError:
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        """
        Permite saber si el hash fue creado con parámetros antiguos
        (muy útil para migraciones futuras)
        """
        return self._hasher.check_needs_rehash(password_hash)


    '''
    hasher = PasswordHasher()
    
    password_hash = hasher.hash_password("1234")
    
    user = {
        "user": "user1",
        "display_name": "User test 1",
        "password_hash": password_hash,
        "active": True
    }
    
    def authenticate(provider, username, password):
    user = provider.get_user(username)
    if not user or not user["active"]:
        return False

    hasher = PasswordHasher()

    if not hasher.verify_password(user["password_hash"], password):
        return False

    return True


    def add_user(self, username, display_name, plain_password):
        hasher = PasswordHasher()
    
        user = {
            "user": username,
            "display_name": display_name,
            "password_hash": hasher.hash_password(plain_password),
            "active": True
        }
    
        self._users.append(user)
        self.save_users()

    '''