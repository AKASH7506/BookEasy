from datetime import datetime
from .firebase import db


# =========================
# COLLECTION NAMES
# =========================

USERS = "users"
PRODUCTS = "products"
SERVICES = "services"
BOOKINGS = "bookings"
MAINTENANCE_PLANS = "maintenance_plans"
TECHNICIAN_APPLICATIONS = "technician_applications"
FEEDBACK = "feedback"


# =========================
# BASIC HELPERS
# =========================

def get_document(collection_name, document_id):
    """
    Get one Firestore document.
    """
    ref = db.collection(collection_name).document(str(document_id))
    snapshot = ref.get()

    if not snapshot.exists:
        return None

    return snapshot.to_dict()


def set_document(collection_name, document_id, data):
    """
    Create or replace a Firestore document.
    """
    ref = db.collection(collection_name).document(str(document_id))
    ref.set(data)

    return data


def update_document(collection_name, document_id, data):
    """
    Update selected fields of a Firestore document.
    """
    ref = db.collection(collection_name).document(str(document_id))
    ref.update(data)

    return get_document(collection_name, document_id)


def delete_document(collection_name, document_id):
    """
    Delete a Firestore document.
    """
    ref = db.collection(collection_name).document(str(document_id))
    ref.delete()


def get_all_documents(collection_name):
    """
    Return all documents from a collection.
    """
    documents = db.collection(collection_name).stream()

    result = []

    for document in documents:
        data = document.to_dict()
        data["_doc_id"] = document.id
        result.append(data)

    return result