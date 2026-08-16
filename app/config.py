import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    groq_api_key: str
    model_name: str

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.groq_api_key = api_key
        self.model_name = os.getenv("MODEL_NAME")
        #"llama-3.3-70b-versatile"


settings = Settings()