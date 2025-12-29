# 📚 Bookstore — Flask Web Application

## Description

A pet project built with Flask that represents an online bookstore.
Users can browse books, add them to a cart, place orders, and leave reviews.

---

## 🚀 Features

- User authentication (register / login)
- Book catalogue with categories and search
- Shopping cart (guest & authenticated users)
- Order system with order history
- Book reviews and rating system

---
## 🛠 Tech Stack

- Python 3.10+
- Flask
- Flask-Login
- Flask-WTF
- SQLAlchemy
- PostgreSQL
- Jinja2
- Bootstrap

--


## Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL
- Virtual environment (recommended)

---


### Installing

1. Clone the repository:

bash
git clone https://github.com/your-username/bookstore.git
cd bookstore

2. Copy code
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
Install dependencies:

3. Copy code
pip install -r requirements.txt


4. Create .env file:

DATABASE_URL=postgresql://user:password@localhost/bookstore_db
SECRET_KEY=your-secret-key

5. Initialize and fill the database (optional):

flask fill_book_db


### Executing program
flask run

The application will be available at:
http://127.0.0.1:5000

## Authors
https://github.com/anniebeva

## Version History

* 0.1
    * Initial Release

##📌 Future improvements

- Unit tests
- Improve account editting function, add 'forget function'
- Email confirmation
- Admin panel
