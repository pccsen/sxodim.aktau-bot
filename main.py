import asyncio
import uvicorn
from fastapi import FastAPI
from app.bot.bot import start_bot
from app.database.database import engine
from app.models.base import Base
import signal

app = FastAPI(title="Event Bot API")

@app.get("/")
async def root():
    return {"message": "Event Bot API"}

# Создание таблиц базы данных
Base.metadata.create_all(bind=engine)

async def shutdown(signal, loop):
    print(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def handle_exit():
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )

async def main():
    # Запускаем aiogram-бота как задачу
    bot_task = asyncio.create_task(start_bot())
    # Запускаем FastAPI через uvicorn в асинхронном режиме
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())
    # Ждём завершения обеих задач
    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    handle_exit()
    asyncio.run(main()) 