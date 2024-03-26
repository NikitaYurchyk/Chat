import aiosqlite
import datetime
import bcrypt
import hashlib

class AsyncDatabase:
    def __init__(self, users_db="users.db", messages_db="messages.db"):
        self.users_db = users_db
        self.messages_db = messages_db

    async def _execute(self, query, parameters=None, db_path=None):
        db_path = db_path or self.users_db
        try:
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(query, parameters or ())
                await db.commit()
                return await cursor.fetchall()
        except aiosqlite.Error as e:
            print(f"Database error: {e}")
            return None

    async def initialize_db(self):
        users_table = """CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )"""
        messages_table = """CREATE TABLE IF NOT EXISTS messages (
            date TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL
        )"""
        await self._execute(users_table, db_path=self.users_db)
        await self._execute(messages_table, db_path=self.messages_db)

    async def addUser(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        await self._execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

    async def sendMessage(self, sender, receiver, message):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_hash = hashlib.sha256(message.encode()).hexdigest()
        await self._execute(
            "INSERT INTO messages (date, sender, receiver, message) VALUES (?, ?, ?, ?)",
            (now, sender, receiver, message_hash),
            db_path=self.messages_db
        )

    async def verifyPassword(self, username, password):
        result = await self._execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        )
        if result:
            hashed_password = result[0][0]
            return bcrypt.checkpw(password.encode(), hashed_password)
        else:
            return False

