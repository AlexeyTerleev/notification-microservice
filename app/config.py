from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseModel):
    RABBIT_USER: str
    RABBIT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT: str

    RESET_PASSWORD_QUEUE: str = "reset-password-stream"

    def get_url(self):
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASS}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    rabbit_mq: RabbitMQSettings


settings = Settings()
