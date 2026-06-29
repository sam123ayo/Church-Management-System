from typing import List
from datetime import date
from pydantic import BaseModel, EmailStr


class AttendanceCreate(BaseModel):
    member_ids: List[int]
    date: str

class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "member"

class MemberUpdate(BaseModel):
    full_name: str
    email: str
    phone: str
    gender: str
    department: str

class PaymentCreate(BaseModel):
    type: str   # offering or donation
    amount: int

class PaymentOut(BaseModel):
    id: int
    type: str
    amount: int
    date: date
    member_id: int

class AttendanceMark(BaseModel):
    member_ids: List[int]   # list of members present
    date: date

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

    phone: str
    gender: str
    department: str
    role: str= "member"

class LoginSchema(BaseModel):
    email: str
    password: str

class PaymentSchema(BaseModel):
    type: str
    amount: int

class AttendanceSchema(BaseModel):
    member_id: int
    present: bool

class EventSchema(BaseModel):
    title: str
    description: str
    date: date
class EventCreate(BaseModel):
    title: str
    description: str
    date: date

class UpdateProfile(BaseModel):
    name: str
    email: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    email: str
    new_password: str
    