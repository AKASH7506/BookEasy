from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(default="", max_length=30)
    address: str = Field(default="", max_length=500)
    password: str = Field(min_length=6, max_length=72)

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
    expected_role: str | None = None

class BookingIn(BaseModel):
    service_id: int
    product_brand: str = Field(default="", max_length=100)
    product_model: str = Field(default="", max_length=100)
    address: str = Field(min_length=5, max_length=1000)
    phone: str = Field(min_length=7, max_length=30)
    service_date: str
    service_time: str
    notes: str = Field(default="", max_length=1000)

class MaintenanceIn(BaseModel):
    service_id: int
    frequency: str
    next_date: str

class ProfileIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(default="", max_length=30)
    address: str = Field(default="", max_length=1000)

class TechnicianApplicationIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=5, max_length=1000)
    experience: str = Field(default="", max_length=100)
    skills: str = Field(min_length=2, max_length=500)
    password: str = Field(min_length=6, max_length=72)

class FeedbackIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)
