from sqlalchemy import Column, Integer, String, UniqueConstraint
from models.database import Base


class Client(Base):
    __tablename__ = "client"
    __table_args__ = (UniqueConstraint("membership", name="client_unique"),)

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    membership = Column(Integer, nullable=False)
