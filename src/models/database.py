import os

from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Table, create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker

load_dotenv()

class Base(DeclarativeBase, MappedAsDataclass):
    pass

engine = create_engine(os.getenv('DB_URL'), echo=True)

interest_sectors = Table(
    "interest_sectors",
    Base.metadata,
    Column("interest_id", ForeignKey("interests.id")),
    Column("sector_id", ForeignKey("sectors.id"))
)

def Session():
    return sessionmaker(bind=engine)()