from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from services.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    
    customers = relationship("Customer", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    __table_args__ = (UniqueConstraint('name', 'user_id', name='unique_customer_per_user'),)
    
    user = relationship("User", back_populates="customers")
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    due_date = Column(Date, nullable=True)
    measurements = Column(Text)
    image_url = Column(String, nullable=True)
    garment_type = Column(String, nullable=True, default="general")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  # ← ADD THIS LINE
    
    customer = relationship("Customer", back_populates="orders")
    user = relationship("User", back_populates="orders")