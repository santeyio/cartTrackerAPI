from __future__ import absolute_import

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data import settings

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

engine = create_engine(settings.DB_DSN)
Session = sessionmaker(bind=engine)
