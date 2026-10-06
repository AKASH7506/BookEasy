# BookEasy API

Base URL: `http://127.0.0.1:8000/api`

## Authentication
- POST `/auth/register` — customer registration
- POST `/auth/login` — login; accepts `expected_role` as `customer`, `admin`, or `technician`
- GET `/me` — current user
- PUT `/me` — update profile

## Catalogue
- GET `/products`
- GET `/services`

## Customer
- POST `/bookings`
- GET `/bookings`
- GET `/bookings/{id}`
- POST `/maintenance`
- GET `/maintenance`

## Admin
- GET `/admin/stats`
- GET `/admin/bookings`
- GET `/admin/users`
- GET `/admin/technicians`
- PATCH `/admin/bookings/{id}?status=Confirmed`
- PATCH `/admin/bookings/{id}/assign?technician_id=3`

## Technician
- GET `/technician/stats`
- GET `/technician/bookings`
- PATCH `/technician/bookings/{id}?status=In%20Progress`
- PATCH `/technician/bookings/{id}?status=Completed`

## Health
- GET `/health`
