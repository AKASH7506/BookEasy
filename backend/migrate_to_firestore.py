from datetime import datetime

from app.database import SessionLocal
from app.models import (
    User,
    Product,
    Service,
    Booking,
    MaintenancePlan,
    TechnicianApplication,
    Feedback,
)
from app.firestore_db import set_document


def migrate_users(db):
    users = db.query(User).all()

    for user in users:
        data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone or "",
            "address": user.address or "",
            "password_hash": user.password_hash,
            "role": user.role or "customer",
            "created_at": user.created_at or datetime.utcnow(),
        }

        set_document("users", user.id, data)

    print(f"Users migrated: {len(users)}")


def migrate_products(db):
    products = db.query(Product).all()

    for product in products:
        data = {
            "id": product.id,
            "name": product.name,
            "icon": product.icon or "service",
            "description": product.description or "",
            "active": product.active,
        }

        set_document("products", product.id, data)

    print(f"Products migrated: {len(products)}")


def migrate_services(db):
    services = db.query(Service).all()

    for service in services:
        data = {
            "id": service.id,
            "product_id": service.product_id,
            "name": service.name,
            "description": service.description or "",
            "price": service.price or 0,
            "duration": service.duration or "1–2 hours",
            "active": service.active,
        }

        set_document("services", service.id, data)

    print(f"Services migrated: {len(services)}")


def migrate_bookings(db):
    bookings = db.query(Booking).all()

    for booking in bookings:
        data = {
            "id": booking.id,
            "booking_code": booking.booking_code,
            "customer_id": booking.customer_id,
            "technician_id": booking.technician_id,
            "service_id": booking.service_id,
            "product_brand": booking.product_brand or "",
            "product_model": booking.product_model or "",
            "address": booking.address,
            "phone": booking.phone,
            "service_date": booking.service_date,
            "service_time": booking.service_time,
            "notes": booking.notes or "",
            "total": booking.total or 0,
            "status": booking.status or "Pending",
            "payment_status": booking.payment_status or "Pay after service",
            "created_at": booking.created_at or datetime.utcnow(),
        }

        set_document("bookings", booking.id, data)

    print(f"Bookings migrated: {len(bookings)}")


def migrate_maintenance_plans(db):
    plans = db.query(MaintenancePlan).all()

    for plan in plans:
        data = {
            "id": plan.id,
            "customer_id": plan.customer_id,
            "service_id": plan.service_id,
            "frequency": plan.frequency or "Quarterly",
            "next_date": plan.next_date,
            "active": plan.active,
        }

        set_document("maintenance_plans", plan.id, data)

    print(f"Maintenance plans migrated: {len(plans)}")


def migrate_technician_applications(db):
    applications = db.query(TechnicianApplication).all()

    for application in applications:
        data = {
            "id": application.id,
            "name": application.name,
            "email": application.email,
            "phone": application.phone,
            "address": application.address or "",
            "experience": application.experience or "",
            "skills": application.skills or "",
            "password_hash": application.password_hash,
            "status": application.status or "Pending",
            "reviewed_at": application.reviewed_at,
            "created_at": application.created_at or datetime.utcnow(),
        }

        set_document(
            "technician_applications",
            application.id,
            data,
        )

    print(
        f"Technician applications migrated: "
        f"{len(applications)}"
    )


def migrate_feedback(db):
    feedback_list = db.query(Feedback).all()

    for feedback in feedback_list:
        data = {
            "id": feedback.id,
            "booking_id": feedback.booking_id,
            "customer_id": feedback.customer_id,
            "rating": feedback.rating,
            "comment": feedback.comment or "",
            "created_at": feedback.created_at or datetime.utcnow(),
        }

        set_document("feedback", feedback.id, data)

    print(f"Feedback migrated: {len(feedback_list)}")


def main():
    print("=" * 50)
    print("BookEasy SQLite → Firestore Migration")
    print("=" * 50)

    db = SessionLocal()

    try:
        migrate_users(db)
        migrate_products(db)
        migrate_services(db)
        migrate_bookings(db)
        migrate_maintenance_plans(db)
        migrate_technician_applications(db)
        migrate_feedback(db)

        print("=" * 50)
        print("Migration completed successfully!")
        print("=" * 50)

    except Exception as e:
        print("=" * 50)
        print("Migration failed!")
        print(f"Error: {e}")
        print("=" * 50)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()