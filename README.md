# BookEasy — Online Product Service Booking System

BookEasy is an industrial-style product service booking platform. The customer already owns the product; BookEasy does not sell or deliver a new product. It connects customers, administrators and field technicians for repair, servicing, installation, parts support and routine maintenance.

## Main improvements in v3
- Customer-friendly catalogue with **14 product categories**.
- Search bar for quickly finding a product.
- Realistic inline SVG product symbols instead of emoji/AI-looking product art.
- Symptom-based service options for customers who do not know the internal fault.
- A **Not Sure — Diagnose** option for every appropriate product.
- No public service-price tags; final cost is confirmed after inspection.
- Technician application workflow: apply → admin review → approve/reject → technician access.
- Admin dashboard for technician applications, bookings and assignments.
- Customer service history with post-completion star rating and feedback.
- Cleaner BookEasy logo and professional footer.
- Demo credentials removed from Admin and Technician login pages.
- Configurable initial administrator through `.env`.

## Portals
### Customer
Register → search product → choose symptom/service → book visit → track status → view technician → submit feedback after completion.

### Admin
Secure login → review technician applications → approve/reject → view bookings → assign technician → update booking status → view field team.

### Technician
Apply with real details → wait for admin approval → login after approval → view assigned jobs → start job → complete job.

## Stack
- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: FastAPI + SQLAlchemy
- Database: SQLite by default; MySQL supported through `DATABASE_URL`
- Authentication: JWT
- Password hashing: Passlib + bcrypt 4.3.0
- API docs: `/docs`

## Run on Windows
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/`.

## Initial administrator
Set your own administrator details in `backend/.env` before first run:
```env
ADMIN_EMAIL=your-email@example.com
ADMIN_NAME=Your Name
ADMIN_PASSWORD=YourStrongPassword
```
The Admin and Technician login pages do not display credentials.

## Service workflow
```text
Customer
  → Search owned product
  → Choose symptom/service or Diagnose
  → Schedule visit
  → Booking created
       ↓
Admin
  → Review request
  → Assign approved technician
       ↓
Technician
  → View assigned job
  → Start service
  → Complete service
       ↓
Customer
  → Sees Completed status
  → Leaves rating + feedback
```
