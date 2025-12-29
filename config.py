from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    APP_PORT: int
    DEBUG: bool = False

    class Config:
        env_file = ".env"


BOOK_CATEGORIES = {
    'Fiction': ['Novel', 'Detective', 'Fantasy', 'Adventure', 'Science Fiction', 'Romance'],
    'Non-fiction': ['History', 'Biography', 'Psychology', 'Science'],
    'Children': ['Children', 'Young Adult'],
    'Business': ['Business', 'Economics', 'Finance', 'Self-help'],
    'Education': ['Education', 'Textbook', 'Learning'],
    'Foreign': ['Foreign', 'Language'],
    'Comics & Mangas': ['Comics', 'Manga'],
}


settings = Settings()