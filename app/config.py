import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")

        self.model_name = os.getenv(
            "MODEL_NAME",
            "llama-3.1-8b-instant",
        )


settings = Settings()

#"llama-3.3-70b-versatile"
