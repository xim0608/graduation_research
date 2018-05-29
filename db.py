from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

engine = create_engine('sqlite:///sample_db.sqlite3', echo=True)

Base = declarative_base()

class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    uid = Column(String(255))
    title = Column(String(255))
    content = Column(Text)
    rating = Column(Integer)

    def __repr__(self):
        return "<Reviews(id={}, uid={}, title={}, content={}, rating={})>"\
            .format(self.id, self.uid, self.title, self.content, self.rating)