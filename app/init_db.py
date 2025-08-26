from app.database import engine, Base
from app import models

def init_db():
    print("Creating tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("Done! tables created")

if __name__ == "__main__":
    init_db()