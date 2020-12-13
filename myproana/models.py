from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"), echo=True)


def create_table(engine):
    Base.metadata.create_all(engine)


class Thread(Base):
    __tablename__ = "thread"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', String(150), unique=True)
    url = Column('url', String(150), unique=False)
    startdate = Column('startdate', String(20), unique=False)
    subforum_id = Column(Integer, ForeignKey('subforum.id'))
    author_id = Column(Integer, ForeignKey('author.id'))
    posts = relationship('Post', backref='thread')


class Subforum(Base):
    __tablename__ = "subforum"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), unique=True)
    threads = relationship('Thread', backref='subforum')


class Post(Base):
    __tablename__ = "post"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    content = Column('content', Text(), unique=False, nullable=True)
    date = Column('date', String(20), unique=False)
    sign = Column('sign', String(10), unique=False, nullable=True)
    noposts = Column('noposts', Integer, unique=False, nullable=True)
    author_id = Column(Integer, ForeignKey('author.id'))
    thread_id = Column(Integer, ForeignKey('thread.id'))


class Author(Base):
    __tablename__ = "author"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), unique=True)
    posts = relationship('Post', backref='author')
    threads = relationship('Thread', backref='author')
    authorinfs = relationship('Authorinfo', backref='author')


class Authorinfo(Base):
    __tablename__ = "authorinfo"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    type = Column('type', Text(), unique=False, nullable=True)
    author_id = Column(Integer, ForeignKey('author.id'))




