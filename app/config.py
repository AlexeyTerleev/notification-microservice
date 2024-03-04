import logging
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    
class RabbitMQSettings(BaseModel):
    RABBIT_USER: str
    RABBIT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT: str

    RESET_PASSWORD_QUEUE: str = "reset-password-stream"
    DEAD_LETTER_QUEUE: str = "dead-letter"

    @property
    def url(self):
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASS}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"
    

class MongoDBSettings(BaseModel):
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_AUTH_SRC: str

    def get_url(self):
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/?authSource={settings.mongo_db.MONGO_AUTH_SRC}"

    
class AWS(BaseModel):
    AWS_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    rabbit_mq: RabbitMQSettings
    mongo_db: MongoDBSettings
    aws: AWS


settings = Settings()
