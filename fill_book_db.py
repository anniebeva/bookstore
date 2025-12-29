import csv
from app.database import session_scope
from app.models import Book, Genre, Stock
import random

DEFAULT_QTY = 3
DEFAULT_COVERS = [
    'img/book_cover1.jpg',
    'img/book_cover2.jpg',
    'img/book_cover3.jpg',
]

with session_scope() as session:
    genres_cache = {}

    with open('book_catalog_sample.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, quotechar='"')
        for row in reader:
            genres_names = [g.strip() for g in row['genre'].split(',')]
            genre_obj = []
            for name in genres_names:
                if name in genres_cache:
                    genre = genres_cache[name]
                else:
                    genre = session.query(Genre).filter_by(name=name).first()
                    if not genre:
                        genre = Genre(name=name)
                        session.add(genre)
                        session.flush()
                    genres_cache[name] = genre
                genre_obj.append(genre)


            book = Book(
                title=row['title'],
                author=row['author'],
                year=row['year'],
                price=row['price'],
                rating = row['rating'],
                cover=random.choice(DEFAULT_COVERS),
                description=row.get('description', None),
                genres=genre_obj
            )
            session.add(book)
            session.flush()

            stock = Stock(
                book_id = book.id,
                quantity = DEFAULT_QTY
            )
            session.add(stock)

    print('books added')
