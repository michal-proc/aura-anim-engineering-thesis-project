"""Password hashing and verification."""

import bcrypt


class PasswordManager:
    """Handles password hashing and verification using bcrypt."""
    
    def __init__(self, rounds: int = 12) -> None:
        """
        Args:
            rounds: Cost factor for bcrypt
        """
        self.rounds = rounds
    
    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Bcrypt hashed password string
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hash to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
