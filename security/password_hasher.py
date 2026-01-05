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