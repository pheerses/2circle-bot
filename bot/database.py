import aiosqlite

DB_PATH = "data/users.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 10,
            is_not_used BOOLEAN DEFAULT TRUE
        )
        """)
        await db.commit()

async def get_balance(user_id: int) -> tuple[int, bool]:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, balance, is_not_used) 
            VALUES (?, 10, TRUE)
        """, (user_id,))
        await db.commit()

        async with db.execute("SELECT balance, is_not_used FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                balance, is_not_used = row
                return balance, bool(is_not_used)
            return 0, False

async def decrement_balance(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        balance = (await get_balance(user_id))[0]
        if balance > 0:
            await db.execute("""
                UPDATE users SET balance = balance - 1, is_not_used = FALSE WHERE user_id = ?
            """, (user_id,))
            await db.commit()
            return True
        return False
