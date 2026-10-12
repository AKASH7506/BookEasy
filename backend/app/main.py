from .models import User
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, text, inspect
from datetime import datetime, date
import os, secrets


from .schemas import RegisterIn, LoginIn, BookingIn, MaintenanceIn, ProfileIn, TechnicianApplicationIn, FeedbackIn
from .auth import hash_password, verify_password, create_token, current_user, admin_user
from .firestore_db import get_all_documents, get_document, set_document


app = FastAPI(
    title="BookEasy API",
    version="3.0.0",
    description="Product service booking and field-service operations platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

FRONT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../frontend")
)

@app.on_event("startup")
def startup():
    print("BookEasy backend started.")


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





@app.on_event("startup")
def startup():
    print("BookEasy backend started.")


@app.get("/api/health")
def health(): return {"status":"ok","service":"BookEasy API","version":"3.0.0"}


from types import SimpleNamespace

@app.post("/api/auth/register")
def register(data: RegisterIn):
    email = str(data.email).lower().strip()
    users = get_all_documents("users")

    # Prevent duplicate accounts
    if any(
        user.get("email", "").lower() == email
        for user in users
    ):
        raise HTTPException(400, "Email already registered")

    # Generate a unique numeric user ID
    next_id = max(
        (int(user.get("id", 0)) for user in users),
        default=0
    ) + 1

    user_data = {
        "id": next_id,
        "name": data.name,
        "email": email,
        "phone": data.phone,
        "address": data.address,
        "password_hash": hash_password(data.password),
        "role": "customer",
        "created_at": datetime.utcnow().isoformat()
    }

    # Save using the numeric ID as the Firestore document ID
    set_document("users", next_id, user_data)

    token_user = SimpleNamespace(id=next_id)

    return {
        "access_token": create_token(token_user),
        "user": {
            "id": next_id,
            "name": data.name,
            "email": email,
            "role": "customer"
        }
    }


@app.post("/api/auth/login")
def login(data: LoginIn):
    email = str(data.email).lower().strip()
    users = get_all_documents("users")

    user = next(
        (
            item for item in users
            if item.get("email", "").lower() == email
        ),
        None
    )

    if not user or not verify_password(
        data.password,
        user.get("password_hash", "")
    ):
        raise HTTPException(401, "Invalid email or password")

    if data.expected_role and user.get("role") != data.expected_role:
        raise HTTPException(
            403,
            f"This account is not a {data.expected_role} account"
        )

    user_id = user.get("id")

    if user_id is None:
        raise HTTPException(500, "User record has no ID")

    token_user = SimpleNamespace(id=user_id)

    return {
        "access_token": create_token(token_user),
        "user": {
            "id": user_id,
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "role": user.get("role", "customer")
        }
    }


@app.get("/api/me")
def me(u:User=Depends(current_user)): return {"id":u.id,"name":u.name,"email":u.email,"phone":u.phone,"address":u.address,"role":u.role}



@app.put("/api/me")
def update_me(
    data: ProfileIn,
    u: User = Depends(current_user)
):
    users = get_all_documents("users")

    user_data = next(
        (
            user for user in users
            if str(user.get("id")) == str(u.id)
        ),
        None
    )

    if not user_data:
        raise HTTPException(404, "User not found")

    user_data["name"] = data.name
    user_data["phone"] = data.phone
    user_data["address"] = data.address

    set_document("users", u.id, user_data)

    return {"message": "Profile updated successfully"}




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
                "id": s.get("id"),
                "name": s.get("name", "Service"),
                "description": s.get("description", ""),
                "duration": s.get("duration", "1–2 hours")
            }
            for s in active_services
            if str(s.get("product_id")) == str(p.get("id"))
        ]

        result.append({
            "id": p.get("id"),
            "name": p.get("name", "Product"),
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
        str(p.get("id")): p.get("name", "Unknown Product")
        for p in products_data
    }

    result = []

    for s in services_data:
        if not s.get("active", True):
            continue

        product_id = s.get("product_id")

        result.append({
            "id": s.get("id"),
            "product_id": product_id,
            "product": product_map.get(
                str(product_id),
                "Unknown Product"
            ),
            "name": s.get("name", "Service"),
            "description": s.get("description", ""),
            "duration": s.get("duration", "1–2 hours")
        })

    result.sort(
        key=lambda x: (
            str(x["product_id"]),
            int(x["id"] or 0)
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
def my_bookings(u: User = Depends(current_user)):

    bookings = get_all_documents("bookings")
    services_data = get_all_documents("services")
    products_data = get_all_documents("products")
    users_data = get_all_documents("users")
    feedback_data = get_all_documents("feedback")

    service_map = {
        str(s["id"]): s
        for s in services_data
    }

    product_map = {
        str(p["id"]): p
        for p in products_data
    }

    user_map = {
        str(user["id"]): user
        for user in users_data
    }

    result = []

    for b in bookings:

        if str(b.get("customer_id")) != str(u.id):
            continue

        service = service_map.get(str(b.get("service_id")), {})
        product = product_map.get(str(service.get("product_id")), {})

        technician = None

        if b.get("technician_id"):
            tech = user_map.get(str(b["technician_id"]))
            if tech:
                technician = {
                    "id": tech.get("id"),
                    "name": tech.get("name"),
                    "phone": tech.get("phone")
                }

        feedback = None

        for f in feedback_data:
            if str(f.get("booking_id")) == str(b.get("id")):
                feedback = {
                    "id": f.get("id"),
                    "booking_id": f.get("booking_id"),
                    "rating": f.get("rating"),
                    "comment": f.get("comment"),
                    "created_at": f.get("created_at")
                }
                break

        result.append({
            "id": b.get("id"),
            "booking_code": b.get("booking_code"),
            "service": service.get("name", ""),
            "product": product.get("name", ""),
            "date": b.get("service_date"),
            "time": b.get("service_time"),
            "address": b.get("address"),
            "phone": b.get("phone"),
            "brand": b.get("product_brand"),
            "model": b.get("product_model"),
            "notes": b.get("notes"),
            "status": b.get("status", "Pending"),
            "payment_status": b.get("payment_status"),
            "technician": technician,
            "feedback": feedback,
            "created_at": b.get("created_at")
        })

    result.sort(
        key=lambda x: str(x.get("id", "")),
        reverse=True
    )

    return result



@app.get("/api/bookings/{booking_id}")
def get_booking(
    booking_id: int,
    u: User = Depends(current_user)
):
    bookings = get_all_documents("bookings")

    b = next(
        (
            booking for booking in bookings
            if str(booking.get("id")) == str(booking_id)
        ),
        None
    )

    if not b:
        raise HTTPException(404, "Booking not found")

    # Check booking access
    if (
        str(b.get("customer_id")) != str(u.id)
        and u.role != "admin"
        and str(b.get("technician_id")) != str(u.id)
    ):
        raise HTTPException(404, "Booking not found")

    services = get_all_documents("services")
    products = get_all_documents("products")
    users = get_all_documents("users")
    feedback_items = get_all_documents("feedback")

    service = next(
        (s for s in services
         if str(s.get("id")) == str(b.get("service_id"))),
        {}
    )

    product = next(
        (p for p in products
         if str(p.get("id")) == str(service.get("product_id"))),
        {}
    )

    technician = next(
        (x for x in users
         if str(x.get("id")) == str(b.get("technician_id"))),
        None
    )

    feedback = next(
        (f for f in feedback_items
         if str(f.get("booking_id")) == str(b.get("id"))),
        None
    )

    return {
        "id": b.get("id"),
        "booking_code": b.get("booking_code"),
        "service": service.get("name", "Service"),
        "product": product.get("name", "Product"),
        "date": b.get("service_date"),
        "time": b.get("service_time"),
        "address": b.get("address"),
        "phone": b.get("phone"),
        "brand": b.get("product_brand"),
        "model": b.get("product_model"),
        "notes": b.get("notes"),
        "status": b.get("status", "Pending"),
        "payment_status": b.get("payment_status"),
        "technician": (
            {
                "id": technician.get("id"),
                "name": technician.get("name"),
                "phone": technician.get("phone")
            }
            if technician else None
        ),
        "feedback": (
            {
                "id": feedback.get("id"),
                "booking_id": feedback.get("booking_id"),
                "rating": feedback.get("rating"),
                "comment": feedback.get("comment"),
                "created_at": feedback.get("created_at")
            }
            if feedback else None
        ),
        "created_at": b.get("created_at")
    }




@app.post("/api/bookings/{booking_id}/feedback")
def create_feedback(
    booking_id: int,
    data: FeedbackIn,
    u: User = Depends(current_user)
):
    # Find the booking in Firestore
    bookings = get_all_documents("bookings")

    booking = next(
        (
            b for b in bookings
            if str(b.get("id")) == str(booking_id)
        ),
        None
    )

    if not booking or str(booking.get("customer_id")) != str(u.id):
        raise HTTPException(404, "Booking not found")

    if booking.get("status") != "Completed":
        raise HTTPException(
            400,
            "Feedback is available after service completion"
        )

    # Check whether feedback already exists
    feedback_items = get_all_documents("feedback")

    if any(
        str(f.get("booking_id")) == str(booking_id)
        for f in feedback_items
    ):
        raise HTTPException(
            400,
            "Feedback already submitted for this booking"
        )

    # Generate a new feedback ID
    next_id = max(
        (int(f.get("id", 0)) for f in feedback_items),
        default=0
    ) + 1

    feedback_data = {
        "id": next_id,
        "booking_id": booking_id,
        "customer_id": u.id,
        "rating": data.rating,
        "comment": data.comment.strip(),
        "created_at": datetime.utcnow()
    }

    set_document("feedback", next_id, feedback_data)

    return {
        "id": next_id,
        "booking_id": booking_id,
        "rating": data.rating,
        "comment": data.comment.strip(),
        "created_at": feedback_data["created_at"].isoformat()
    }




@app.post("/api/maintenance")
def maintenance(
    data: MaintenanceIn,
    u: User = Depends(current_user)
):
    if u.role != "customer":
        raise HTTPException(
            403,
            "Only customers can create maintenance plans"
        )

    # Verify service exists in Firestore
    service = get_document("services", data.service_id)

    if not service or not service.get("active", True):
        raise HTTPException(404, "Service not found")

    # Get existing maintenance plans
    plans = get_all_documents("maintenance_plans")

    next_id = max(
        (int(plan.get("id", 0)) for plan in plans),
        default=0
    ) + 1

    plan_data = {
        "id": next_id,
        "customer_id": u.id,
        "service_id": data.service_id,
        "frequency": data.frequency,
        "next_date": data.next_date,
        "active": True,
        "created_at": datetime.utcnow().isoformat()
    }

    # Save plan to Firestore
    set_document("maintenance_plans", next_id, plan_data)

    return {
        "id": next_id,
        "message": "Maintenance plan created successfully"
    }




@app.get("/api/maintenance")
def maintenance_list(
    u: User = Depends(current_user)
):
    if u.role != "customer":
        return []

    # Read maintenance plans from Firestore
    plans = get_all_documents("maintenance_plans")
    services = get_all_documents("services")

    service_map = {
        str(service.get("id")): service
        for service in services
    }

    result = []

    for plan in plans:
        if str(plan.get("customer_id")) != str(u.id):
            continue

        if not plan.get("active", True):
            continue

        service = service_map.get(
            str(plan.get("service_id")), {}
        )

        result.append({
            "id": plan.get("id"),
            "service": service.get("name", "Service"),
            "frequency": plan.get("frequency", ""),
            "next_date": plan.get("next_date")
        })

    return result




@app.post("/api/technician-applications")
def apply_technician(data: TechnicianApplicationIn):
    email = str(data.email).lower().strip()

    # Check registered users in Firestore
    users = get_all_documents("users")

    if any(
        user.get("email", "").lower().strip() == email
        for user in users
    ):
        raise HTTPException(
            400,
            "This email is already registered"
        )

    # Check existing applications
    applications = get_all_documents(
        "technician_applications"
    )

    existing = next(
        (
            a for a in applications
            if a.get("email", "").lower().strip() == email
        ),
        None
    )

    if existing and existing.get("status") == "Pending":
        raise HTTPException(
            400,
            "A technician application is already under review"
        )

    # Generate or reuse application ID
    if existing:
        application_id = int(existing["id"])
    else:
        application_id = max(
            (int(a.get("id", 0)) for a in applications),
            default=0
        ) + 1

    application_data = {
        "id": application_id,
        "name": data.name,
        "email": email,
        "phone": data.phone,
        "address": data.address,
        "experience": data.experience,
        "skills": data.skills,
        "password_hash": hash_password(data.password),
        "status": "Pending",
        "created_at": datetime.utcnow().isoformat(),
        "reviewed_at": None
    }

    set_document(
        "technician_applications",
        application_id,
        application_data
    )

    return {
        "message": (
            "Application submitted. The admin will review "
            "your details before technician access is activated."
        ),
        "application_id": application_id
    }


@app.get("/api/technician-applications")
def technician_applications(
    _: User = Depends(admin_user)
):
    applications = get_all_documents("technician_applications")

    applications.sort(
        key=lambda a: int(a.get("id") or 0),
        reverse=True
    )

    return [
        {
            "id": a.get("id"),
            "name": a.get("name", ""),
            "email": a.get("email", ""),
            "phone": a.get("phone", ""),
            "address": a.get("address", ""),
            "experience": a.get("experience", ""),
            "skills": a.get("skills", ""),
            "status": a.get("status", "Pending"),
            "created_at": (
                a.get("created_at").isoformat()
                if hasattr(a.get("created_at"), "isoformat")
                else a.get("created_at")
            )
        }
        for a in applications
    ]




@app.patch("/api/technician-applications/{application_id}")
def review_technician_application(
    application_id: int,
    status: str,
    u: User = Depends(admin_user)
):
    if status not in {"Approved", "Rejected"}:
        raise HTTPException(400, "Invalid application status")

    # Get applications from Firestore
    applications = get_all_documents("technician_applications")

    application = next(
        (
            a for a in applications
            if str(a.get("id")) == str(application_id)
        ),
        None
    )

    if not application:
        raise HTTPException(404, "Application not found")

    if application.get("status") != "Pending":
        raise HTTPException(
            400,
            "Application has already been reviewed"
        )

    if status == "Approved":
        users = get_all_documents("users")
        email = application.get("email", "").strip().lower()

        # Check whether the applicant is already registered
        if any(
            user.get("email", "").strip().lower() == email
            for user in users
        ):
            raise HTTPException(
                400,
                "Applicant email is already registered"
            )

        # Generate a new user ID
        next_user_id = max(
            (int(user.get("id", 0)) for user in users),
            default=0
        ) + 1

        technician_data = {
            "id": next_user_id,
            "name": application.get("name", ""),
            "email": email,
            "phone": application.get("phone", ""),
            "address": application.get("address", ""),
            "password_hash": application.get("password_hash", ""),
            "role": "technician",
            "created_at": datetime.utcnow().isoformat()
        }

        # Save technician account in Firestore
        set_document("users", next_user_id, technician_data)

    # Update application status in Firestore
    application["status"] = status
    application["reviewed_at"] = datetime.utcnow().isoformat()

    set_document(
        "technician_applications",
        application_id,
        application
    )

    return {
        "message": f"Technician application {status.lower()}",
        "status": status
    }



@app.get("/api/admin/stats")
def stats(_: User = Depends(admin_user)):
    users = get_all_documents("users")
    bookings = get_all_documents("bookings")
    applications = get_all_documents("technician_applications")

    return {
        "customers": sum(
            1 for user in users
            if user.get("role") == "customer"
        ),
        "technicians": sum(
            1 for user in users
            if user.get("role") == "technician"
        ),
        "bookings": len(bookings),
        "pending": sum(
            1 for booking in bookings
            if booking.get("status") == "Pending"
        ),
        "active_jobs": sum(
            1 for booking in bookings
            if booking.get("status") in ["Assigned", "In Progress"]
        ),
        "pending_applications": sum(
            1 for application in applications
            if application.get("status") == "Pending"
        )
    }



@app.get("/api/admin/bookings")
def admin_bookings(_: User = Depends(admin_user)):
    bookings = get_all_documents("bookings")
    users = get_all_documents("users")
    services = get_all_documents("services")
    products = get_all_documents("products")

    user_map = {
        str(user.get("id")): user
        for user in users
    }
    service_map = {
        str(service.get("id")): service
        for service in services
    }
    product_map = {
        str(product.get("id")): product
        for product in products
    }

    result = []

    for b in bookings:
        service = service_map.get(str(b.get("service_id")), {})
        product = product_map.get(str(service.get("product_id")), {})
        customer = user_map.get(str(b.get("customer_id")), {})

        technician = user_map.get(str(b.get("technician_id")))
        technician_data = None

        if technician:
            technician_data = {
                "id": technician.get("id"),
                "name": technician.get("name"),
                "phone": technician.get("phone")
            }

        result.append({
            "id": b.get("id"),
            "booking_code": b.get("booking_code"),
            "service": service.get("name", "Service"),
            "product": product.get("name", "Product"),
            "date": b.get("service_date"),
            "time": b.get("service_time"),
            "address": b.get("address"),
            "phone": b.get("phone"),
            "brand": b.get("product_brand"),
            "model": b.get("product_model"),
            "notes": b.get("notes"),
            "status": b.get("status", "Pending"),
            "payment_status": b.get("payment_status"),
            "technician": technician_data,
            "feedback": None,
            "created_at": b.get("created_at"),
            "customer": customer.get("name", "Unknown customer"),
            "customer_email": customer.get("email", "")
        })

    result.sort(
        key=lambda item: int(item.get("id") or 0),
        reverse=True
    )

    return result


@app.get("/api/admin/technicians")
def admin_technicians(_: User = Depends(admin_user)):
    users = get_all_documents("users")
    bookings = get_all_documents("bookings")

    technicians = [
        user for user in users
        if user.get("role") == "technician"
    ]

    result = []

    for technician in technicians:
        active_jobs = sum(
            1 for booking in bookings
            if str(booking.get("technician_id"))
            == str(technician.get("id"))
            and booking.get("status") in {"Assigned", "In Progress"}
        )

        result.append({
            "id": technician.get("id"),
            "name": technician.get("name", ""),
            "email": technician.get("email", ""),
            "phone": technician.get("phone", ""),
            "address": technician.get("address", ""),
            "active_jobs": active_jobs
        })

    result.sort(key=lambda technician: technician["name"].lower())
    return result



@app.patch("/api/admin/bookings/{booking_id}")
def admin_update(
    booking_id: int,
    status: str,
    u: User = Depends(admin_user)
):
    allowed = {
        "Pending",
        "Confirmed",
        "Assigned",
        "In Progress",
        "Completed",
        "Cancelled"
    }

    if status not in allowed:
        raise HTTPException(400, "Invalid status")

    # Find booking in Firestore
    bookings = get_all_documents("bookings")

    booking = next(
        (
            b for b in bookings
            if str(b.get("id")) == str(booking_id)
        ),
        None
    )

    if not booking:
        raise HTTPException(404, "Booking not found")

    # Update booking status
    booking["status"] = status
    booking["updated_at"] = datetime.utcnow().isoformat()

    set_document("bookings", booking_id, booking)

    return {
        "id": booking.get("id"),
        "booking_code": booking.get("booking_code"),
        "status": booking.get("status"),
        "message": "Booking status updated successfully"
    }




@app.patch("/api/admin/bookings/{booking_id}/assign")
def assign_booking(
    booking_id: int,
    technician_id: int,
    u: User = Depends(admin_user)
):
    # Get the booking from Firestore
    bookings = get_all_documents("bookings")

    booking = next(
        (
            b for b in bookings
            if str(b.get("id")) == str(booking_id)
        ),
        None
    )

    if not booking:
        raise HTTPException(404, "Booking not found")

    # Find the technician in Firestore
    users = get_all_documents("users")

    technician = next(
        (
            user for user in users
            if str(user.get("id")) == str(technician_id)
        ),
        None
    )

    if not technician or technician.get("role") != "technician":
        raise HTTPException(400, "Invalid technician")

    # Assign the technician
    booking["technician_id"] = technician.get("id")

    if booking.get("status") in {"Pending", "Confirmed"}:
        booking["status"] = "Assigned"

    booking["updated_at"] = datetime.utcnow().isoformat()

    set_document("bookings", booking_id, booking)

    return {
        "id": booking.get("id"),
        "booking_code": booking.get("booking_code"),
        "technician": {
            "id": technician.get("id"),
            "name": technician.get("name"),
            "phone": technician.get("phone")
        },
        "status": booking.get("status"),
        "message": "Technician assigned successfully"
    }




@app.get("/api/admin/users")
def admin_users(
    _: User = Depends(admin_user)
):
    users = get_all_documents("users")

    result = [
        {
            "id": user.get("id"),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "phone": user.get("phone", ""),
            "role": user.get("role", "customer"),
            "address": user.get("address", "")
        }
        for user in users
    ]

    result.sort(
        key=lambda user: int(user.get("id") or 0),
        reverse=True
    )

    return result




@app.get("/api/technician/stats")
def technician_stats(u: User = Depends(current_user)):
    if u.role != "technician":
        raise HTTPException(403, "Technician access required")

    jobs = [
        booking
        for booking in get_all_documents("bookings")
        if str(booking.get("technician_id")) == str(u.id)
    ]

    return {
        "assigned": sum(
            1 for booking in jobs
            if booking.get("status") == "Assigned"
        ),
        "in_progress": sum(
            1 for booking in jobs
            if booking.get("status") == "In Progress"
        ),
        "completed": sum(
            1 for booking in jobs
            if booking.get("status") == "Completed"
        ),
        "total": len(jobs)
    }


@app.get("/api/technician/bookings")
def technician_bookings(
    u: User = Depends(current_user)
):
    if u.role != "technician":
        raise HTTPException(403, "Technician access required")

    bookings = get_all_documents("bookings")
    users = get_all_documents("users")
    services = get_all_documents("services")
    products = get_all_documents("products")
    feedback_items = get_all_documents("feedback")

    user_map = {
        str(user.get("id")): user for user in users
    }
    service_map = {
        str(service.get("id")): service for service in services
    }
    product_map = {
        str(product.get("id")): product for product in products
    }

    result = []

    for b in bookings:
        if str(b.get("technician_id")) != str(u.id):
            continue

        service = service_map.get(
            str(b.get("service_id")), {}
        )
        product = product_map.get(
            str(service.get("product_id")), {}
        )
        customer = user_map.get(
            str(b.get("customer_id")), {}
        )

        technician_feedback = next(
            (
                f for f in feedback_items
                if str(f.get("booking_id")) == str(b.get("id"))
            ),
            None
        )

        result.append({
            "id": b.get("id"),
            "booking_code": b.get("booking_code"),
            "service": service.get("name", "Service"),
            "product": product.get("name", "Product"),
            "date": b.get("service_date"),
            "time": b.get("service_time"),
            "address": b.get("address"),
            "phone": b.get("phone"),
            "brand": b.get("product_brand"),
            "model": b.get("product_model"),
            "notes": b.get("notes"),
            "status": b.get("status", "Pending"),
            "payment_status": b.get("payment_status"),
            "technician": {
                "id": u.id,
                "name": getattr(u, "name", ""),
                "phone": getattr(u, "phone", "")
            },
            "feedback": (
                {
                    "id": technician_feedback.get("id"),
                    "booking_id": technician_feedback.get("booking_id"),
                    "rating": technician_feedback.get("rating"),
                    "comment": technician_feedback.get("comment"),
                    "created_at": technician_feedback.get("created_at")
                }
                if technician_feedback else None
            ),
            "created_at": b.get("created_at"),
            "customer": customer.get("name", "Unknown customer"),
            "customer_email": customer.get("email", "")
        })

    result.sort(
        key=lambda item: int(item.get("id") or 0),
        reverse=True
    )

    return result



@app.patch("/api/technician/bookings/{booking_id}")
def technician_update(
    booking_id: int,
    status: str,
    u: User = Depends(current_user)
):
    if u.role != "technician":
        raise HTTPException(403, "Technician access required")

    allowed = {"Assigned", "In Progress", "Completed"}

    if status not in allowed:
        raise HTTPException(
            400,
            "Technician cannot set that status"
        )

    bookings = get_all_documents("bookings")

    booking = next(
        (
            b for b in bookings
            if str(b.get("id")) == str(booking_id)
        ),
        None
    )

    if (
        not booking
        or str(booking.get("technician_id")) != str(u.id)
    ):
        raise HTTPException(404, "Assigned job not found")

    booking["status"] = status
    booking["updated_at"] = datetime.utcnow().isoformat()

    set_document("bookings", booking_id, booking)

    return {
        "id": booking.get("id"),
        "booking_code": booking.get("booking_code"),
        "status": booking.get("status"),
        "message": "Booking status updated successfully"
    }

app.mount(
    "/",
    StaticFiles(directory=FRONT, html=True),
    name="frontend"
)
