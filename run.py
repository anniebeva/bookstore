from app import app
from app.database import init_db
from config import settings

if __name__ == '__main__':
    init_db()
    app.run(port=settings.APP_PORT, debug=settings.DEBUG)