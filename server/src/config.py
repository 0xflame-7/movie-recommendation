from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  DB_URL: str

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
  )

  def __init__(self, **data):
    super().__init__(**data)


Config = Settings()
