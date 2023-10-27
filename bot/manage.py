from aiogram import executor

from config import dp

from handlers import *

async def on_startup(_):
	print("Бот запущен")

if __name__ == "__main__":
	executor.start_polling(
			dispatcher = dp,
			skip_updates = True,
			on_startup = on_startup,
		)