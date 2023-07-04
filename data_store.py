import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, MetaData
from config import DSN

engine = create_engine(DSN)
metadata = MetaData()
Base = declarative_base()

class Diplom(Base):
    __tablename__ = 'diplom'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, primary_key=True)

def add_user(engine, profile_id, user_id):
    with Session(engine) as session:
        to_bd = Diplom(profile_id=profile_id, user_id=user_id)
        session.add(to_bd)
        session.commit()

def check_user(engine, profile_id, user_id):
    with Session(engine) as session:
        from_bd = session.query(Diplom).filter(
            Diplom.profile_id == profile_id,
            Diplom.user_id == user_id
        ).all()
        return True if from_bd else False

if __name__ == '__main__':
    engine = create_engine(DSN)
    Base.metadata.create_all(engine)
    add_user(engine, 2113, 124512)
    res = check_user(engine, 2113, 1245121)
    print(res)
