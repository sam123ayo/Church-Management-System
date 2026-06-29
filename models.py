from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base


# =========================
# USER TABLE
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True)

    password = Column(String, nullable=False)

    role = Column(String, default="member")

    profile_picture = Column(String, nullable=True)

    # NEW FIELDS
    phone = Column(String)

    gender = Column(String)

    department = Column(String)

    # RELATIONSHIPS
    payments = relationship("Payment", back_populates="member")

    attendance = relationship("Attendance", back_populates="member")


# =========================
# PAYMENT TABLE
# =========================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    type = Column(String)

    amount = Column(Integer)

    date = Column(Date)

    member_id = Column(Integer, ForeignKey("users.id"))

    member = relationship("User", back_populates="payments")


# =========================
# ATTENDANCE TABLE
# =========================

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)

    date = Column(Date)

    present = Column(Boolean, default=False)

    member_id = Column(Integer, ForeignKey("users.id"))

    member = relationship("User", back_populates="attendance")


# =========================
# EVENTS TABLE
# =========================

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    description = Column(String)

    date = Column(Date)


# =========================
# EVENT ATTENDANCE
# =========================

class EventAttendance(Base):
    __tablename__ = "event_attendance"

    id = Column(Integer, primary_key=True)

    event_id = Column(Integer, ForeignKey("events.id"))

    member_id = Column(Integer, ForeignKey("users.id"))