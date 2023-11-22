import os

from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

load_dotenv()
username = os.getenv("DB_USERNAME")
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
dbname = os.getenv('DB_NAME')
DSN = f'postgresql://{username}:{password}@{host}/{dbname}'

Base = declarative_base()


# def create_tables(engine):
#     # delete all previous data
#     # Base.metadata.drop_all(engine)
#     # Make tables
#     Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer)
    prompt = sq.Column(sq.TEXT)
    bot = sq.Column(sq.TEXT)
    counter = sq.Column(sq.Integer)


engine = create_engine(DSN)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def get_or_create_user(user_id):
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.counter += 1
    else:
        user = User(username=user_id, counter=1)
        session.add(user)
    return user
