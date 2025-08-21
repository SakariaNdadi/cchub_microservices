from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from database import Base


class Todo(Base):
    __tablename__ = "todos_todo"  # This MUST match Django's table name

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(10), nullable=False, default="DRAFT")
    remind_at = Column(DateTime, nullable=False)
    location_name = Column(String(255), default="Windhoek, Namibia")
    latitude = Column(Float, default=22.5649)
    longitude = Column(Float, default=17.0842)
    created_at = Column(DateTime, nullable=False)
    profile_id = Column(Integer, ForeignKey("accounts_profile.id"))
