from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "l2sec-api"
    app_env: str = "local"
    api_v1_prefix: str = "/v1"
    database_url: str = "postgresql+psycopg2://l2sec:l2sec@localhost:5432/l2sec"

    class Config:
        env_file = ".env"


settings = Settings()