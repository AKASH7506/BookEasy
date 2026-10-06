from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, text, inspect
from datetime import datetime, date
import os, secrets

from .database import Base, engine, get_db
from .models import User, Product, Service, Booking, MaintenancePlan, TechnicianApplication, Feedback
from .schemas import RegisterIn, LoginIn, BookingIn, MaintenanceIn, ProfileIn, TechnicianApplicationIn, FeedbackIn
from .auth import hash_password, verify_password, create_token, current_user, admin_user
from .firestore_db import get_all_documents, get_document, set_document
Base.metadata.create_all(bind=engine)
app = FastAPI(title="BookEasy API", version="3.0.0", description="Product service booking and field-service operations platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
FRONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

PRODUCT_DATA = {
    "Air Conditioner": ("ac", "Cooling, repair, cleaning, installation and gas-related service", [
        ("Routine Service", "Regular cleaning, filter check, drain check and performance inspection", "Best for scheduled maintenance or reduced cooling."),
        ("Not Cooling / Low Cooling", "Technician checks airflow, coils, refrigerant and other cooling causes", "Choose this when the AC is running but cooling is weak or absent."),
        ("Water Leakage", "Drain line, indoor unit and moisture-related diagnosis", "Choose this when water is dripping or collecting indoors."),
        ("Noise / Vibration", "Fan, mounting and internal component inspection", "Choose this for unusual sound, vibration or rattling."),
        ("Gas / Refrigerant Check", "Leak inspection and refrigerant-related service", "Choose this when cooling is very low or a gas issue is suspected."),
        ("Installation / Uninstallation", "Professional installation or safe removal of the AC", "For a new location, shifting, or removal."),
        ("Not Sure — Diagnose My AC", "Complete fault diagnosis before deciding the exact repair", "Best choice when you do not know what is wrong."),
    ]),
    "Washing Machine": ("washing-machine", "Repair, routine maintenance, drainage and parts support", [
        ("Routine Servicing", "Cleaning, drum, inlet, drain and general performance check", "For regular maintenance or an older machine."),
        ("Not Starting / Power Issue", "Electrical, switch, board and power-path diagnosis", "Choose this when the machine does not start."),
        ("Not Draining / Water Issue", "Drain pump, hose, inlet and water-flow diagnosis", "Choose this when water remains inside or does not fill correctly."),
        ("Excess Noise / Vibration", "Balance, bearing, drum and suspension inspection", "Choose this when the machine shakes or makes unusual noise."),
        ("Door / Lid Problem", "Lock, hinge, sensor and door/lid mechanism inspection", "For door or lid not closing, opening or locking correctly."),
        ("Parts Replacement", "Faulty component inspection and replacement service", "The technician confirms the exact part after diagnosis."),
        ("Not Sure — Diagnose My Washing Machine", "Full diagnostic inspection before repair", "Best choice when you cannot identify the fault."),
    ]),
    "Refrigerator": ("refrigerator", "Cooling, compressor, electrical, ice and routine maintenance", [
        ("Routine Service", "Cleaning, temperature, gasket and performance inspection", "For preventive maintenance."),
        ("Not Cooling / Low Cooling", "Cooling-system and temperature-control diagnosis", "Choose this when food is not cooling properly."),
        ("Water / Ice Problem", "Drain, ice maker and water-flow inspection", "For excess water, blocked drainage or ice-making issues."),
        ("Unusual Noise", "Fan, compressor and vibration diagnosis", "Choose this for humming, clicking or unusual sounds."),
        ("Excess Frost / Ice", "Defrost, airflow and temperature-control diagnosis", "For abnormal ice or frost build-up."),
        ("Gas / Cooling System Check", "Leak and refrigeration-system inspection", "Technician confirms whether refrigerant service is actually required."),
        ("Not Sure — Diagnose My Refrigerator", "Complete fault diagnosis", "Best choice when you do not know the internal problem."),
    ]),
    "Television": ("television", "Display, sound, power, smart-TV and board diagnostics", [
        ("TV Diagnosis", "Complete inspection of power, display, sound and controls", "Best choice when the fault is unclear."),
        ("No Power / Not Turning On", "Power supply, board and connection diagnosis", "Choose this when the TV does not turn on."),
        ("No Picture / Display Problem", "Panel, backlight and display-signal diagnosis", "For black screen, lines, dim picture or display faults."),
        ("Sound Problem", "Speaker, audio circuit and software diagnosis", "For no sound, low sound or distorted audio."),
        ("Smart TV / Software Service", "App, update, connectivity and software troubleshooting", "For smart features, apps or software issues."),
        ("Remote / Connectivity Issue", "Remote pairing, sensor and connection troubleshooting", "For remote or device connectivity problems."),
    ]),
    "Laptop": ("laptop", "Hardware, software, performance, cleaning and component support", [
        ("Laptop Diagnosis", "Complete hardware and software inspection", "Best choice when the exact problem is unknown."),
        ("Slow / Hanging / Overheating", "Performance, storage, memory and thermal diagnosis", "For slow performance, freezing or excessive heat."),
        ("Windows / Software Service", "Operating system, driver and software troubleshooting", "For software errors, updates or configuration issues."),
        ("Screen / Display Problem", "Display, cable and panel diagnosis", "For flickering, lines, black screen or damaged display."),
        ("Battery / Charging Problem", "Battery health, charger and charging-circuit diagnosis", "For fast battery drain or charging issues."),
        ("Cleaning & Thermal Maintenance", "Internal dust cleaning and thermal maintenance", "Recommended when the laptop overheats or needs preventive care."),
    ]),
    "Smartphone": ("smartphone", "Screen, battery, charging, software and hardware support", [
        ("Phone Diagnosis", "Complete hardware and software fault inspection", "Best choice when the exact issue is unknown."),
        ("Screen / Display Problem", "Display, touch and screen-component diagnosis", "For cracked, black, flickering or touch issues."),
        ("Battery / Fast Drain", "Battery health and charging-system diagnosis", "For rapid battery drain, swelling or poor battery life."),
        ("Charging Problem", "Port, cable, charging circuit and battery diagnosis", "For slow, intermittent or failed charging."),
        ("Software / Performance Service", "OS, app, update and performance troubleshooting", "For crashes, slowness, updates or software errors."),
        ("Speaker / Mic / Camera Problem", "Hardware component diagnosis", "For audio, microphone or camera faults."),
    ]),
    "Water Purifier": ("water-purifier", "Filter, membrane, leakage, water-flow and purification service", [
        ("Routine Service", "Filter, membrane, water flow and general inspection", "For regular maintenance."),
        ("Poor Water Flow", "Filter blockage, inlet and pump/flow diagnosis", "For slow or reduced water output."),
        ("Bad Taste / Odour", "Filter and purification-stage inspection", "For changes in taste, smell or water quality."),
        ("Water Leakage", "Pipe, valve, tank and fitting inspection", "For visible leakage or dripping."),
        ("Filter / Membrane Replacement", "Component inspection and replacement", "Technician confirms the required component before replacement."),
        ("Not Sure — Diagnose My Purifier", "Complete purification-system diagnosis", "Best choice when the issue is unclear."),
    ]),
    "Microwave": ("microwave", "Heating, power, control panel and safety-related service", [
        ("Routine Inspection", "Cleaning, heating and general safety inspection", "For preventive maintenance."),
        ("Not Heating", "Magnetron, power path and control diagnosis", "Choose this when the microwave runs but does not heat."),
        ("Not Starting / Power Issue", "Power supply, fuse, door switch and board diagnosis", "For complete power/start-up problems."),
        ("Sparking / Unusual Sound", "Safety inspection and internal fault diagnosis", "Stop using the appliance if sparking occurs and book this service."),
        ("Door / Control Problem", "Door mechanism and control-panel diagnosis", "For door, buttons or display issues."),
        ("Not Sure — Diagnose My Microwave", "Full diagnostic inspection", "Best choice when you cannot identify the problem."),
    ]),
    "Mixer Grinder": ("mixer-grinder", "Motor, jar, blade, noise, power and performance service", [
        ("Routine Service", "Cleaning, blade, jar coupling and motor inspection", "For regular maintenance."),
        ("Not Starting / Power Issue", "Switch, cord, motor and electrical diagnosis", "For a mixer that does not start."),
        ("Low Speed / Weak Grinding", "Motor, blade, coupling and performance diagnosis", "For reduced speed or poor grinding."),
        ("Excess Noise / Vibration", "Blade, jar coupling and motor inspection", "For unusual sound or shaking."),
        ("Jar / Blade Problem", "Jar lock, blade and coupling inspection", "For leakage, loose jar or blade-related issues."),
        ("Burning Smell / Overheating", "Motor and electrical safety diagnosis", "Stop using the appliance if burning smell or overheating occurs."),
        ("Not Sure — Diagnose My Mixer Grinder", "Complete diagnostic inspection", "Best choice when the internal issue is unknown."),
    ]),
    "Ceiling Fan": ("ceiling-fan", "Motor, regulator, capacitor, noise and installation service", [
        ("Routine Service", "Cleaning, electrical and mechanical inspection", "For preventive maintenance."),
        ("Not Starting / Slow Speed", "Power, capacitor, regulator and motor diagnosis", "For a fan that does not start or rotates slowly."),
        ("Noise / Wobbling", "Blade balance, bearing and mounting inspection", "For vibration, wobbling or unusual noise."),
        ("Regulator / Speed Problem", "Regulator and speed-control diagnosis", "For speed not changing correctly."),
        ("Capacitor / Motor Check", "Electrical component diagnosis and replacement if required", "Technician confirms the faulty component."),
        ("Installation / Removal", "Safe installation, removal and balancing", "For a new installation or shifting."),
    ]),
    "Water Heater": ("water-heater", "Heating, thermostat, leakage, electrical and safety service", [
        ("Routine Safety Service", "Tank, wiring, thermostat and safety inspection", "Recommended for preventive maintenance."),
        ("Not Heating / Low Heating", "Heating element, thermostat and power diagnosis", "For water not heating properly."),
        ("Water Leakage", "Tank, valve, pipe and fitting inspection", "For visible water leakage."),
        ("Electrical / Tripping Problem", "Wiring, element and safety-device diagnosis", "For repeated electrical trips or shocks; technician checks safety first."),
        ("Noise / Pressure Problem", "Tank, pressure and heating-system diagnosis", "For unusual noise or pressure-related symptoms."),
        ("Installation / Removal", "Safe installation, removal and connection check", "For installation or relocation."),
        ("Not Sure — Diagnose My Water Heater", "Complete safety and fault diagnosis", "Best choice when the cause is unknown."),
    ]),
    "Vacuum Cleaner": ("vacuum-cleaner", "Suction, motor, filter, brush and electrical service", [
        ("Routine Service", "Filter, brush, hose and motor inspection", "For preventive maintenance."),
        ("Low / No Suction", "Filter, hose, brush and motor diagnosis", "For weak or absent suction."),
        ("Not Starting / Power Issue", "Cord, switch, motor and electrical diagnosis", "For a vacuum that does not start."),
        ("Overheating / Burning Smell", "Motor, airflow and electrical safety diagnosis", "Stop using the cleaner and book a safety inspection."),
        ("Noise / Brush Problem", "Motor, bearing and brush inspection", "For unusual sound or brush movement issues."),
        ("Not Sure — Diagnose My Vacuum Cleaner", "Complete diagnostic inspection", "Best choice when the issue is unclear."),
    ]),
    "Clothes Iron": ("clothes-iron", "Heating, thermostat, power cord and steam service", [
        ("Routine Service", "Soleplate, thermostat, cord and general inspection", "For preventive maintenance."),
        ("Not Heating", "Heating element, thermostat and power diagnosis", "For an iron that stays cold."),
        ("Overheating / Temperature Problem", "Thermostat and safety-control diagnosis", "For excessive heat or incorrect temperature."),
        ("Steam / Water Leakage", "Steam holes, tank and valve inspection", "For weak steam, no steam or leakage."),
        ("Power / Cord Problem", "Cable, plug and electrical safety diagnosis", "For intermittent or failed power."),
        ("Not Sure — Diagnose My Iron", "Complete diagnostic inspection", "Best choice when you do not know the cause."),
    ]),
}


def seed(db: Session):
    for name, (icon, desc, services) in PRODUCT_DATA.items():
        p = db.query(Product).filter(Product.name == name).first()
        if not p:
            p = Product(name=name, icon=icon, description=desc)
            db.add(p); db.flush()
        else:
            p.icon, p.description, p.active = icon, desc, True
        existing = {s.name: s for s in p.services}
        for idx, (sn, sd, help_text) in enumerate(services):
            s = existing.get(sn)
            if not s:
                s = Service(product_id=p.id, name=sn, description=f"{sd} {help_text}", price=0, duration="1–3 hours")
                db.add(s)
            else:
                s.description = f"{sd} {help_text}"; s.active = True
    # One real administrator is provisioned for initial system ownership.
    admin_email = os.getenv("ADMIN_EMAIL", "admin@bookeasy.com").lower()
    admin_name = os.getenv("ADMIN_NAME", "BookEasy Administrator")
    admin_password = os.getenv("ADMIN_PASSWORD", "ChangeThisAdminPassword")
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        db.add(User(name=admin_name, email=admin_email, password_hash=hash_password(admin_password), role="admin", phone="", address="BookEasy Service Center"))
    # A starter approved technician keeps local development/testing possible; no demo credentials are displayed in the UI.
    tech = db.query(User).filter(User.email == "tech@bookeasy.com").first()
    if not tech:
        db.add(User(name="Rajesh Kumar", email="tech@bookeasy.com", password_hash=hash_password("Tech@123"), role="technician", phone="9876543211", address="Durgapur Service Zone"))
    db.commit()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try: seed(db)
    finally: db.close()

@app.get("/api/health")
def health(): return {"status":"ok","service":"BookEasy API","version":"3.0.0"}

@app.post("/api/auth/register")
def register(data:RegisterIn, db:Session=Depends(get_db)):
    email=data.email.lower()
    if db.query(User).filter(User.email==email).first(): raise HTTPException(400,"Email already registered")
    u=User(name=data.name,email=email,phone=data.phone,address=data.address,password_hash=hash_password(data.password),role="customer")
    db.add(u); db.commit(); db.refresh(u)
    return {"access_token":create_token(u),"user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}

@app.post("/api/auth/login")
def login(data:LoginIn, db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==data.email.lower()).first()
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Invalid email or password")
    if data.expected_role and u.role != data.expected_role: raise HTTPException(403,f"This account is not a {data.expected_role} account")
    return {"access_token":create_token(u),"user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}

@app.get("/api/me")
def me(u:User=Depends(current_user)): return {"id":u.id,"name":u.name,"email":u.email,"phone":u.phone,"address":u.address,"role":u.role}

@app.put("/api/me")
def update_me(data:ProfileIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    u.name=data.name;u.phone=data.phone;u.address=data.address;db.commit();return {"message":"Profile updated"}

@app.get("/api/products")
def products():
    products_data = get_all_documents("products")
    services_data = get_all_documents("services")

    active_products = [
        p for p in products_data
        if p.get("active", True)
    ]

    active_services = [
        s for s in services_data
        if s.get("active", True)
    ]

    result = []

    for p in active_products:
        product_services = [
            {
                "id": s["id"],
                "name": s["name"],
                "description": s.get("description", ""),
                "duration": s.get("duration", "1–2 hours")
            }
            for s in active_services
            if s.get("product_id") == p["id"]
        ]

        result.append({
            "id": p["id"],
            "name": p["name"],
            "icon": p.get("icon", "service"),
            "description": p.get("description", ""),
            "services": product_services
        })

    result.sort(key=lambda x: x["name"].lower())

    return result
@app.get("/api/services")
def services():
    products_data = get_all_documents("products")
    services_data = get_all_documents("services")

    product_map = {
        p["id"]: p["name"]
        for p in products_data
    }

    result = []

    for s in services_data:
        if not s.get("active", True):
            continue

        result.append({
            "id": s["id"],
            "product_id": s["product_id"],
            "product": product_map.get(
                s["product_id"],
                "Unknown Product"
            ),
            "name": s["name"],
            "description": s.get("description", ""),
            "duration": s.get(
                "duration",
                "1–2 hours"
            )
        })

    result.sort(
        key=lambda x: (
            x["product_id"],
            x["id"]
        )
    )

    return result
@app.post("/api/bookings")
def create_booking(
    data: BookingIn,
    u: User = Depends(current_user)
):
    if u.role != "customer":
        raise HTTPException(
            403,
            "Only customers can create bookings"
        )

    # Get service from Firestore
    service = get_document(
        "services",
        data.service_id
    )

    if not service or not service.get("active", True):
        raise HTTPException(
            404,
            "Service not found"
        )

    # Validate service date
    try:
        selected = date.fromisoformat(
            data.service_date
        )

        if selected < date.today():
            raise HTTPException(
                400,
                "Service date cannot be in the past"
            )

    except ValueError:
        raise HTTPException(
            400,
            "Invalid service date"
        )

    # Generate booking code
    code = "BK-" + secrets.token_hex(4).upper()

    # Generate next booking ID
    existing_bookings = get_all_documents(
        "bookings"
    )

    if existing_bookings:
        next_id = max(
            b.get("id", 0)
            for b in existing_bookings
        ) + 1
    else:
        next_id = 1

    # Booking data
    booking_data = {
        "id": next_id,
        "booking_code": code,
        "customer_id": u.id,
        "technician_id": None,
        "service_id": service["id"],
        "product_brand": data.product_brand,
        "product_model": data.product_model,
        "address": data.address,
        "phone": data.phone,
        "service_date": data.service_date,
        "service_time": data.service_time,
        "notes": data.notes,
        "total": 0,
        "status": "Pending",
        "payment_status": "Pay after service",
        "created_at": datetime.utcnow()
    }

    # Save booking to Firestore
    set_document(
        "bookings",
        next_id,
        booking_data
    )

    return {
        "id": next_id,
        "booking_code": code,
        "service": service["name"],
        "status": "Pending",
        "message": "Booking created successfully"
    }
def feedback_out(f):
    return {"id":f.id,"booking_id":f.booking_id,"rating":f.rating,"comment":f.comment,"created_at":f.created_at.isoformat() if f.created_at else None}

def booking_out(b):
    return {"id":b.id,"booking_code":b.booking_code,"service":b.service.name,"product":b.service.product.name,"date":b.service_date,"time":b.service_time,"address":b.address,"phone":b.phone,"brand":b.product_brand,"model":b.product_model,"notes":b.notes,"status":b.status,"payment_status":b.payment_status,"technician":({"id":b.technician.id,"name":b.technician.name,"phone":b.technician.phone} if b.technician else None),"feedback":feedback_out(b.feedback) if b.feedback else None,"created_at":b.created_at.isoformat() if b.created_at else None}

@app.get("/api/bookings")
def my_bookings(u:User=Depends(current_user),db:Session=Depends(get_db)):
    return [booking_out(b) for b in db.query(Booking).filter(Booking.customer_id==u.id).order_by(Booking.id.desc()).all()]

@app.get("/api/bookings/{booking_id}")
def get_booking(booking_id:int,u:User=Depends(current_user),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id)
    if not b or (b.customer_id!=u.id and u.role!="admin" and b.technician_id!=u.id): raise HTTPException(404,"Booking not found")
    return booking_out(b)

@app.post("/api/bookings/{booking_id}/feedback")
def create_feedback(booking_id:int,data:FeedbackIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id)
    if not b or b.customer_id != u.id: raise HTTPException(404,"Booking not found")
    if b.status != "Completed": raise HTTPException(400,"Feedback is available after service completion")
    if b.feedback: raise HTTPException(400,"Feedback already submitted for this booking")
    f=Feedback(booking_id=b.id,customer_id=u.id,rating=data.rating,comment=data.comment.strip())
    db.add(f);db.commit();db.refresh(f);return feedback_out(f)

@app.post("/api/maintenance")
def maintenance(data:MaintenanceIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    if u.role != "customer": raise HTTPException(403,"Only customers can create maintenance plans")
    if not db.get(Service,data.service_id): raise HTTPException(404,"Service not found")
    m=MaintenancePlan(customer_id=u.id,service_id=data.service_id,frequency=data.frequency,next_date=data.next_date);db.add(m);db.commit();return {"message":"Maintenance plan created"}

@app.get("/api/maintenance")
def maintenance_list(u:User=Depends(current_user),db:Session=Depends(get_db)):
    if u.role != "customer": return []
    rows=db.query(MaintenancePlan).filter(MaintenancePlan.customer_id==u.id,MaintenancePlan.active==True).all()
    return [{"id":m.id,"service":db.get(Service,m.service_id).name,"frequency":m.frequency,"next_date":m.next_date} for m in rows]

@app.post("/api/technician-applications")
def apply_technician(data:TechnicianApplicationIn,db:Session=Depends(get_db)):
    email=data.email.lower()
    if db.query(User).filter(User.email==email).first(): raise HTTPException(400,"This email is already registered")
    existing=db.query(TechnicianApplication).filter(TechnicianApplication.email==email).first()
    if existing and existing.status=="Pending": raise HTTPException(400,"A technician application is already under review")
    if existing: db.delete(existing); db.flush()
    a=TechnicianApplication(name=data.name,email=email,phone=data.phone,address=data.address,experience=data.experience,skills=data.skills,password_hash=hash_password(data.password),status="Pending")
    db.add(a);db.commit();db.refresh(a)
    return {"message":"Application submitted. The admin will review your details before technician access is activated.","application_id":a.id}

@app.get("/api/technician-applications")
def technician_applications(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    rows=db.query(TechnicianApplication).order_by(TechnicianApplication.id.desc()).all()
    return [{"id":a.id,"name":a.name,"email":a.email,"phone":a.phone,"address":a.address,"experience":a.experience,"skills":a.skills,"status":a.status,"created_at":a.created_at.isoformat() if a.created_at else None} for a in rows]

@app.patch("/api/technician-applications/{application_id}")
def review_technician_application(application_id:int,status:str,u:User=Depends(admin_user),db:Session=Depends(get_db)):
    if status not in {"Approved","Rejected"}: raise HTTPException(400,"Invalid application status")
    a=db.get(TechnicianApplication,application_id)
    if not a: raise HTTPException(404,"Application not found")
    if a.status != "Pending": raise HTTPException(400,"Application has already been reviewed")
    a.status=status;a.reviewed_at=datetime.utcnow()
    if status=="Approved":
        if db.query(User).filter(User.email==a.email).first(): raise HTTPException(400,"Applicant email is already registered")
        db.add(User(name=a.name,email=a.email,phone=a.phone,address=a.address,password_hash=a.password_hash,role="technician"))
    db.commit();return {"message":f"Technician application {status.lower()}","status":status}

@app.get("/api/admin/stats")
def stats(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    return {"customers":db.query(User).filter(User.role=="customer").count(),"technicians":db.query(User).filter(User.role=="technician").count(),"bookings":db.query(Booking).count(),"pending":db.query(Booking).filter(Booking.status=="Pending").count(),"active_jobs":db.query(Booking).filter(Booking.status.in_(["Assigned","In Progress"])).count(),"pending_applications":db.query(TechnicianApplication).filter(TechnicianApplication.status=="Pending").count()}

@app.get("/api/admin/bookings")
def admin_bookings(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    return [{**booking_out(b),"customer":b.customer.name,"customer_email":b.customer.email} for b in db.query(Booking).order_by(Booking.id.desc()).all()]

@app.get("/api/admin/technicians")
def admin_technicians(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    return [{"id":u.id,"name":u.name,"email":u.email,"phone":u.phone,"address":u.address,"active_jobs":db.query(Booking).filter(Booking.technician_id==u.id,Booking.status.in_(["Assigned","In Progress"])).count()} for u in db.query(User).filter(User.role=="technician").order_by(User.name).all()]

@app.patch("/api/admin/bookings/{booking_id}")
def admin_update(booking_id:int,status:str,u:User=Depends(admin_user),db:Session=Depends(get_db)):
    allowed={"Pending","Confirmed","Assigned","In Progress","Completed","Cancelled"}
    if status not in allowed: raise HTTPException(400,"Invalid status")
    b=db.get(Booking,booking_id)
    if not b: raise HTTPException(404,"Booking not found")
    b.status=status;db.commit();return booking_out(b)

@app.patch("/api/admin/bookings/{booking_id}/assign")
def assign_booking(booking_id:int,technician_id:int,u:User=Depends(admin_user),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id); tech=db.get(User,technician_id)
    if not b: raise HTTPException(404,"Booking not found")
    if not tech or tech.role!="technician": raise HTTPException(400,"Invalid technician")
    b.technician_id=tech.id
    if b.status in {"Pending","Confirmed"}: b.status="Assigned"
    db.commit();db.refresh(b);return booking_out(b)

@app.get("/api/admin/users")
def admin_users(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    return [{"id":u.id,"name":u.name,"email":u.email,"phone":u.phone,"role":u.role,"address":u.address} for u in db.query(User).order_by(User.id.desc()).all()]

@app.get("/api/technician/stats")
def technician_stats(u:User=Depends(current_user),db:Session=Depends(get_db)):
    if u.role!="technician": raise HTTPException(403,"Technician access required")
    jobs=db.query(Booking).filter(Booking.technician_id==u.id)
    return {"assigned":jobs.filter(Booking.status=="Assigned").count(),"in_progress":jobs.filter(Booking.status=="In Progress").count(),"completed":jobs.filter(Booking.status=="Completed").count(),"total":jobs.count()}

@app.get("/api/technician/bookings")
def technician_bookings(u:User=Depends(current_user),db:Session=Depends(get_db)):
    if u.role!="technician": raise HTTPException(403,"Technician access required")
    return [{**booking_out(b),"customer":b.customer.name,"customer_email":b.customer.email} for b in db.query(Booking).filter(Booking.technician_id==u.id).order_by(Booking.id.desc()).all()]

@app.patch("/api/technician/bookings/{booking_id}")
def technician_update(booking_id:int,status:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
    if u.role!="technician": raise HTTPException(403,"Technician access required")
    allowed={"Assigned","In Progress","Completed"}
    if status not in allowed: raise HTTPException(400,"Technician cannot set that status")
    b=db.get(Booking,booking_id)
    if not b or b.technician_id!=u.id: raise HTTPException(404,"Assigned job not found")
    b.status=status;db.commit();db.refresh(b);return booking_out(b)

app.mount("/",StaticFiles(directory=FRONT,html=True),name="frontend")
