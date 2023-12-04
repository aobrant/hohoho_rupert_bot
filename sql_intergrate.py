import os

from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text

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


def get_or_create_user(user_id, bot_name):
    user_id = int(user_id)
    user = session.query(User).filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id, counter=0, prompt="", bot=bot_name)
        session.add(user)
    return user


def increase_counter(user_id):
    try:
        user_id = user_id
        session.query(User).filter(User.user_id == user_id).update({'counter': User.counter + 1})
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error while working with database: {e}")
    finally:
        session.close()
    return "ok"


def re_counter(user_id):
    try:
        user_id = user_id
        session.query(User).filter(User.user_id == user_id).update({'counter': 1})
        session.query(User).filter(User.user_id == user_id).update({'prompt': ""})
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error while working with database: {e}")
    finally:
        session.close()
    return "ok"


def update_prompt(user_id, prompt):
    try:
        user_id = user_id
        current_prompt = session.query(User).filter(User.user_id == user_id).first().prompt
        updated_prompt = current_prompt + prompt
        session.query(User).filter(User.user_id == user_id).update({'prompt': updated_prompt})
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error while working with database: {e}")
    finally:
        session.close()


def get_prompt(user_id):
    try:
        user_id = user_id
        current_prompt = session.query(User).filter(User.user_id == user_id).first().prompt
        return current_prompt
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error while working with database: {e}")
    finally:
        session.close()
