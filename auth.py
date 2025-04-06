from database import DatabaseManager

class AuthManager:
    """
    AuthManager handles user authentication, including user registration,
    login validation, and password hashing with a custom algorithm.
    """

    def __init__(self):
        """
        Initializes the AuthManager instance by creating a connection 
        to the database using DatabaseManager.
        """
        self.db = DatabaseManager(1)  

    def close(self):
        """
        Closes the connection to the database.
        Should be called when the authentication operations are complete.
        """
        self.db.close_connection()

    def custom_hash(self, password: str) -> str:
        """
        Generates a custom hash for a given password by:
        - Appending a salt key fetched from the database.
        - Applying bitwise shift operations on each character.
        - Constraining the hash within a 32-bit range.
        
        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The resulting hexadecimal hash string.
        """
        salt = self.db.get_salt_key()  # Retrieve the salt key from the database
        data = password + salt         # Combine password with salt
        hash_value = 0

        # Apply custom bitwise hash algorithm
        for char in data:
            hash_value = (hash_value << 3) + (hash_value >> 2) + ord(char)
            hash_value %= 2**32  # Limit to 32-bit integer size
        
        return hex(hash_value)  # Convert final hash to hexadecimal string

    def register_user(self, username: str, password: str) -> bool:
        """
        Registers a new user by hashing the password and storing it in the database.

        Args:
            username (str): The desired username for the new user.
            password (str): The plain text password for the new user.

        Returns:
            bool: True if registration was successful, False otherwise.
        """
        hashed_password = self.custom_hash(password)  # Hash the password
        return self.db.add_user(username, hashed_password)  # Add user to database

    def validate_login(self, username: str, password: str) -> str:
        """
        Validates a user's login credentials by:
        - Retrieving the stored hashed password from the database.
        - Hashing the input password using the same algorithm.
        - Comparing both hashes for authentication.

        Args:
            username (str): The username attempting to log in.
            password (str): The plain text password entered by the user.

        Returns:
            str: A message indicating success or the type of login failure.
        """
        user_data = self.db.get_user(username)  # Retrieve user record from DB
        if user_data.empty:
            return "Invalid username"
        
        stored_hashed_password = user_data["hashed_password"][0]  # Get stored hash
        hashed_password = self.custom_hash(password)              # Hash input password
        
        if stored_hashed_password == hashed_password:
            self.db.log_event(username, 'LOGIN', 'User logged in.')
            return "Login Successful" 
        else: 
            self.db.log_event(username, 'LOGIN', 'Login Unsuccessful/Wrong Credentials')
            return "Invalid password"
