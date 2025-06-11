from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
from pydantic import ConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(extra='allow')
    
    # Bot settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "")
    
    def get_admin_ids(self) -> List[int]:
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bot.db")
    
    # Web settings
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "")
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_URL: str = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
    
    # Web server settings
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 8000

settings = Settings() 