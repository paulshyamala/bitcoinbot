from database import DatabaseManager

class AuthManager:
    

    def __init__(self):
        """Initializes the database connection."""
        self.db = DatabaseManager()  

    def close(self):
        """Closes the database connection."""
        self.db.close_connection()

    def custom_hash(self, password: str) -> str:
        """
        Generates a custom hash for a given password using bitwise shifts and a salt from the database.
        """
        salt = self.db.get_salt_key()  # ✅ Uses instance method
        data = password + salt
        hash_value = 0

        for char in data:
            hash_value = (hash_value << 3) + (hash_value >> 2) + ord(char)
            hash_value %= 2**32  # Keep it within 32-bit range
        
        return hex(hash_value)

    def register_user(self, username: str, password: str) -> bool:
        """
        Registers a new user with a hashed password.
        """
        hashed_password = self.custom_hash(password)
        return self.db.add_user(username, hashed_password)  # ✅ Uses instance method

    def validate_login(self, username: str, password: str) -> str:
        """
        Validates user login by checking stored hashed password.
        """
        user_data = self.db.get_user(username)  # ✅ Uses instance method
        if user_data.empty:
            return "Invalid username"
        
        stored_hashed_password = user_data["hashed_password"][0]
        hashed_password = self.custom_hash(password)
        
        if stored_hashed_password == hashed_password:
            self.db.log_event(username, 'LOGIN', 'User logged in.')
            return "Login Successful" 
        else: 
            self.db.log_event(username, 'LOGIN', 'Login Unsuccessful/Wrong Credentials')
            return "Invalid password"
    
    
