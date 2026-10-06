from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(30), default="")
    address = Column(Text, default="")
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="customer")
    created_at = Column(DateTime, default=datetime.utcnow)
    bookings = relationship("Booking", back_populates="customer", foreign_keys="Booking.customer_id")
    assigned_bookings = relationship("Booking", back_populates="technician", foreign_keys="Booking.technician_id")
    feedback = relationship("Feedback", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(40), default="service")
    description = Column(Text, default="")
    active = Column(Boolean, default=True)
    services = relationship("Service", back_populates="product", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False, default=0)
    duration = Column(String(40), default="1–2 hours")
    active = Column(Boolean, default=True)
    product = relationship("Product", back_populates="services")
    bookings = relationship("Booking", back_populates="service")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    product_brand = Column(String(100), default="")
    product_model = Column(String(100), default="")
    address = Column(Text, nullable=False)
    phone = Column(String(30), nullable=False)
    service_date = Column(String(20), nullable=False)
    service_time = Column(String(20), nullable=False)
    notes = Column(Text, default="")
    total = Column(Float, nullable=False, default=0)
    status = Column(String(30), default="Pending")
    payment_status = Column(String(30), default="Pay after service")
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("User", back_populates="bookings", foreign_keys=[customer_id])
    technician = relationship("User", back_populates="assigned_bookings", foreign_keys=[technician_id])
    service = relationship("Service", back_populates="bookings")
    feedback = relationship("Feedback", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class MaintenancePlan(Base):
    __tablename__ = "maintenance_plans"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    frequency = Column(String(30), default="Quarterly")
    next_date = Column(String(20), nullable=False)
    active = Column(Boolean, default=True)

class TechnicianApplication(Base):
    __tablename__ = "technician_applications"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=False)
    address = Column(Text, default="")
    experience = Column(String(100), default="")
    skills = Column(Text, default="")
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), default="Pending")
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    booking = relationship("Booking", back_populates="feedback")
    customer = relationship("User", back_populates="feedback")
