# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config import db_url_object


# схема БД
metadata = MetaData()
Base = declarative_base()
engine = create_engine(db_url_object)

class Tools(Base):
    __tablename__ = 'UserVK'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    unique_id = sq.Column(sq.Integer, unique=True)

    def __init__ (self, engine):
        self.engine = engine

# добавление записи в БД
    def add_bd_user (self, profile_id, unique_id):
        with Session(engine) as session:
            to_bd = Tools(profile_id=profile_id, unique_id=unique_id)
            session.add(to_bd)
            session.commit()

# извлечение записей из БД
    def user_check(self, profile_id, unique_id):
        with Session(engine) as session:
            return (session.query(Tools).filter(Tools.profile_id == profile_id, Tools.unique_id == unique_id).first()
            )
# удаление таблицы
    def drop_bd_user(self):
        Base.metadata.drop_all(self)

if __name__ == '_main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)