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


PICKUP_STORES = [
('', 'Select pickup location'),

    (
        'Downtown Books|Main Street 12|Springfield',
        'Downtown Books — Main Street 12, Springfield'
    ),
    (
        'Readers Corner|Oak Avenue 7|Riverdale',
        'Readers Corner — Oak Avenue 7, Riverdale'
    ),
    (
        'Book Haven|Maple Road 45|Hill Valley',
        'Book Haven — Maple Road 45, Hill Valley'
    ),
    (
        'City Library Pickup|Broadway 101|Fairview',
        'City Library Pickup — Broadway 101, Fairview'
    ),
]

settings = Settings()