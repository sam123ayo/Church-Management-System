from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import engine, SessionLocal, Base
from backend import models, schemas, auth
from datetime import date
from sqlalchemy.exc import IntegrityError
import csv
from fastapi.responses import FileResponse
import os
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File
import shutil
from backend.schemas import AttendanceCreate, ChangePassword, ForgotPassword
from backend.auth import create_token, get_current_user, verify_password, hash_password
from backend.auth import router as auth_router



app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ ADD HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

# 🔥 Create database tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home
@app.get("/")
def home():
    return {"message": "Church Management System Running"}

# Register user
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # ✅ Check if email already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.hash_password(user.password)

    new_user = models.User(
    name=user.name,
    email=user.email,
    password=hashed,
    role="admin"
)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

    return {"message": "User registered"}


# ✅ Mark Attendance
@app.post("/attendance/mark")
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db)
):

    for member_id in data.member_ids:

        attendance = models.Attendance(
            member_id=member_id,
            date=data.date
        )

        db.add(attendance)

    db.commit()

    return {"message": "Attendance marked successfully"}


# ✅ Get Absentees
@app.get("/attendance/absentees")
def get_absentees(
    date: date,
    db: Session = Depends(get_db),
    user_id: int = Depends(auth.get_current_user)
):

    users = db.query(models.User).all()

    present_records = db.query(models.Attendance).filter(
        models.Attendance.date == date,
        models.Attendance.present == True
    ).all()

    present_ids = [record.member_id for record in present_records]

    absentees = [user for user in users if user.id not in present_ids]

    return {
        "date": date,
        "absentees": [
            {"id": user.id, "name": user.name, "email": user.email}
            for user in absentees
        ]
    }
def get_absentees(date: date, db: Session = Depends(get_db)):

    users = db.query(models.User).all()

    present_records = db.query(models.Attendance).filter(
        models.Attendance.date == date,
        models.Attendance.present == True
    ).all()

    present_ids = [record.member_id for record in present_records]

    absentees = [user for user in users if user.id not in present_ids]

    return {
        "date": date,
        "absentees": [
            {"id": user.id, "name": user.name, "email": user.email}
            for user in absentees
        ]
    }
@app.get("/members")
def get_members(
    db: Session = Depends(get_db)
):

    members = db.query(models.User).all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone,
            "gender": m.gender,
            "department": m.department,
            "role": m.role
        }
        for m in members
    ]

@app.post("/payments")
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(auth.get_current_user)
):
    new_payment = models.Payment(
        type=payment.type,
        amount=payment.amount,
        date=date.today(),
        member_id=user_id
    )

    db.add(new_payment)
    db.commit()

    return {"message": "Payment successful"}

@app.get("/payments/my")
def get_my_payments(
    db: Session = Depends(get_db),
    user_id: int = Depends(auth.get_current_user)
):
    payments = db.query(models.Payment).filter(
        models.Payment.member_id == user_id
    ).all()

    return payments
@app.get("/payments")
def get_all_payments(
    db: Session = Depends(get_db),
    user_id: int = Depends(auth.get_current_user)
):
    return db.query(models.Payment).all()

@app.post("/make-admin/{user_id}")
def make_admin(user_id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"

    db.commit()

    return {"message": "User is now admin"}

@app.get("/users")
def users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/events")
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.admin_only)
):

    new_event = models.Event(
        title=event.title,
        description=event.description,
        date=event.date
    )

    db.add(new_event)

    db.commit()

    return {"message": "Event created"}

@app.get("/events")
def get_events(db: Session = Depends(get_db)):

    return db.query(models.Event).all()
@app.post("/events/register/{event_id}")

def register_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):

    existing = db.query(models.EventAttendance).filter(
        models.EventAttendance.event_id == event_id,
        models.EventAttendance.member_id == current_user["user_id"]
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already registered"
        )

    attendance = models.EventAttendance(
        event_id=event_id,
        member_id=current_user["user_id"]
    )

    db.add(attendance)

    db.commit()

    return {"message": "Registered successfully"}

@app.delete("/events/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.admin_only)
):

    event = db.query(models.Event).filter(
        models.Event.id == event_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    db.delete(event)

    db.commit()

    return {"message": "Event deleted"}

@app.get("/attendance/export")
def export_absentees(
    date: date,
    db: Session = Depends(get_db),
    current_user = Depends(auth.admin_only)
):

    users = db.query(models.User).all()

    present_records = db.query(models.Attendance).filter(
        models.Attendance.date == date,
        models.Attendance.present == True
    ).all()

    present_ids = [record.member_id for record in present_records]

    absentees = [
        user for user in users
        if user.id not in present_ids
    ]

    # CSV filename
    filename = f"absentees_{date}.csv"

    # Create CSV file
    with open(filename, mode="w", newline="") as file:

        writer = csv.writer(file)

        # Headers
        writer.writerow(["ID", "Name", "Email"])

        # Data
        for user in absentees:

            writer.writerow([
                user.id,
                user.name,
                user.email
            ])

    return FileResponse(
        path=filename,
        filename=filename,
        media_type='text/csv'
    )
@app.get("/profile")
def get_profile(current_user: models.User = Depends(auth.get_current_user)):

    return {
    "id": current_user.id,
    "name": current_user.name,
    "email": current_user.email,
    "role": current_user["role"],
    "profile_picture": current_user.profile_picture
   }

@app.put("/profile/update")
def update_profile(
    data: schemas.UpdateProfile,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    # check if email already exists
    existing = db.query(models.User).filter(
        models.User.email == data.email,
        models.User.id != current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    current_user.name = data.name
    current_user.email = data.email

    db.commit()

    return {"message": "Profile updated successfully"}

@app.post("/profile/upload-picture")
def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    file_path = f"uploads/{current_user.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.profile_picture = file_path

    db.commit()

    return {
        "message": "Profile picture uploaded",
        "image_url": f"http://127.0.0.1:8000/{file_path}"
    }
    
@app.post("/change-password")
def change_password(
    data: ChangePassword,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # check old password
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password incorrect")

    # save new password
    current_user.password = hash_password(data.new_password)

    db.commit()

    return {"message": "Password updated successfully"}

@app.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Account found. You can now reset password."
    }

@app.post("/reset-password")
def reset_password(data: schemas.ResetPassword, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(data.new_password)

    db.commit()

    return {"message": "Password reset successful"}


@app.delete("/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):

    member = db.query(models.Member).filter(
        models.Member.id == member_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    db.delete(member)
    db.commit()

    return {"message": "Member deleted"}


@app.put("/members/{member_id}")
def update_member(
    member_id: int,
    updated_member: schemas.MemberCreate,
    db: Session = Depends(get_db)
):

    member = db.query(models.Member).filter(
        models.Member.id == member_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.full_name = updated_member.full_name
    member.email = updated_member.email
    member.phone = updated_member.phone
    member.gender = updated_member.gender
    member.department = updated_member.department

    db.commit()

    return {"message": "Member updated"}