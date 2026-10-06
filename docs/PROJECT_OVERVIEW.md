# Project Overview — BookEasy

## Core concept
The customer already owns the product. BookEasy is a service-management platform, not an e-commerce delivery system. It handles repair, servicing, installation, parts replacement and routine maintenance.

## User roles
### Customer
- Register/login
- Browse products and services
- Book a service visit
- View estimated service cost
- Track booking status
- See assigned technician details
- Maintain contact information

### Admin
- Dashboard and operational statistics
- View all booking requests
- Assign technicians
- Change booking status
- View customer and technician information

### Technician
- Login to technician portal
- View assigned jobs
- View customer, address, time and issue notes
- Change Assigned → In Progress → Completed

## Technical architecture
```text
Browser UI
   ↓ REST/JSON
FastAPI
   ↓ SQLAlchemy
SQLite / MySQL
```

## Main workflow
```text
Customer request → Admin review → Technician assignment → Field service → Completion → Customer tracking
```

## Production-oriented enhancements included
- Role-based access control
- JWT authentication
- Password hashing
- Server-side validation
- Date validation for bookings
- Technician assignment
- Responsive UI
- Loading/skeleton states
- Toast feedback
- Empty states
- Theme persistence
- SPA-style navigation

## Future production enhancements
- OTP/email verification
- Payment gateway
- SMS/email notifications
- Google Maps/location picker
- Parts inventory and purchase tracking
- Technician availability calendar
- Service invoices and PDF generation
- Ratings and reviews
- Maintenance reminders
- Audit log and role permission matrix
- Database migrations with Alembic
- Deployment with HTTPS and production secrets
