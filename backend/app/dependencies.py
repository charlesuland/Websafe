from app.database import SessionLocal

# These dependencies are what the routes will pull from
# for ex., the functions will ask for a connection to the database; that comes from here


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
