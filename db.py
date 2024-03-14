import aiosqlite
import datetime
import bcrypt
import hashlib

class AsyncDatabase:
    def __init__(self, users_db="users.db", messages_db="messages.db"):
        self.users_db = users_db
        self.messages_db = messages_db

    async def _connect(self, db_path):
        return await aiosqlite.connect(db_path)

    async def _execute(self, db, query, parameters=None):
        try:
            async with db:  # Ensure connection is closed
                cursor = await db.execute(query, parameters or ())
                result = await cursor.fetchall()
                await db.commit()
                return result
        except aiosqlite.Error as e:
            print(f"Database error: {e}")

    async def addUser(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        db = await self._connect(self.users_db)
        return await self._execute(
            db, "INSERT INTO users VALUES (?, ?)", (username, hashed_password)
        )

    async def sendMessage(self, sender, receiver, message):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_hash = hashlib.sha256(message.encode()).hexdigest()  
        db = await self._connect(self.messages_db)
        return await self._execute(
            db,
            "INSERT INTO messages (date, sender, receiver, message) VALUES (?, ?, ?, ?)",
            (now, sender, receiver, message_hash),
        )

    async def verifyPassword(self, username, password):
        db = await self._connect(self.users_db)
        result = await self._execute(
            db, "SELECT password FROM users WHERE username = ?", (username,)
        )
        if result:
            hashed_password = result[0][0]  # Get the stored hash
            return bcrypt.checkpw(password.encode(), hashed_password)
        else:
            return False  # User not found