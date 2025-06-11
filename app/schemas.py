from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import EmailStr
from enum import Enum

# Enums for better type safety
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"

class ShipmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class ShipmentPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class UserBase(SQLModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Relationships
    shipments: List["Shipment"] = Relationship(back_populates="customer")
    notifications: List["Notification"] = Relationship(back_populates="user")

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Optional[str] = None

# --- Shipment Models ---

class ShipmentBase(SQLModel):
    tracking_number: str = Field(index=True, unique=True)
    status: ShipmentStatus = ShipmentStatus.PENDING
    priority: ShipmentPriority = ShipmentPriority.NORMAL
    origin_address: str
    destination_address: str
    origin_city: str
    destination_city: str
    origin_country: str = "USA"
    destination_country: str = "USA"
    weight: float = Field(gt=0, description="Weight in kg")
    dimensions: Optional[str] = Field(default=None, description="LxWxH in cm")
    declared_value: Optional[float] = Field(default=None, gt=0)
    insurance_required: bool = False
    fragile: bool = False
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    customer_id: Optional[int] = Field(default=None, foreign_key="user.id")

class ShipmentCreate(ShipmentBase):
    pass

class Shipment(ShipmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationships
    customer: Optional[User] = Relationship(back_populates="shipments")
    tracking_history: List["TrackingHistory"] = Relationship(back_populates="shipment")
    documents: List["Document"] = Relationship(back_populates="shipment")

class ShipmentRead(ShipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    customer: Optional["UserRead"] = None

class ShipmentUpdate(SQLModel):
    tracking_number: Optional[str] = Field(default=None, index=True, unique=True)
    status: Optional[ShipmentStatus] = Field(default=None)
    priority: Optional[ShipmentPriority] = Field(default=None)
    origin_address: Optional[str] = Field(default=None)
    destination_address: Optional[str] = Field(default=None)
    origin_city: Optional[str] = Field(default=None)
    destination_city: Optional[str] = Field(default=None)
    weight: Optional[float] = Field(default=None, gt=0)
    dimensions: Optional[str] = Field(default=None)
    declared_value: Optional[float] = Field(default=None, gt=0)
    insurance_required: Optional[bool] = Field(default=None)
    fragile: Optional[bool] = Field(default=None)
    description: Optional[str] = Field(default=None)
    special_instructions: Optional[str] = Field(default=None)
    estimated_delivery_date: Optional[datetime] = Field(default=None)
    actual_delivery_date: Optional[datetime] = Field(default=None)

# --- Tracking History Models ---

class TrackingHistoryBase(SQLModel):
    status: ShipmentStatus
    location: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TrackingHistoryCreate(TrackingHistoryBase):
    shipment_id: int

class TrackingHistory(TrackingHistoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shipment_id: int = Field(foreign_key="shipment.id")

    # Relationships
    shipment: Shipment = Relationship(back_populates="tracking_history")

class TrackingHistoryRead(TrackingHistoryBase):
    id: int
    shipment_id: int

# --- Document Models ---

class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CUSTOMS = "customs"
    INSURANCE = "insurance"
    PHOTO = "photo"
    OTHER = "other"

class DocumentBase(SQLModel):
    name: str
    document_type: DocumentType
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class DocumentCreate(DocumentBase):
    shipment_id: int

class Document(DocumentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shipment_id: int = Field(foreign_key="shipment.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    shipment: Shipment = Relationship(back_populates="documents")

class DocumentRead(DocumentBase):
    id: int
    shipment_id: int
    uploaded_at: datetime

# --- Notification Models ---

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class NotificationBase(SQLModel):
    title: str
    message: str
    notification_type: NotificationType
    status: NotificationStatus = NotificationStatus.PENDING

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    # Relationships
    user: User = Relationship(back_populates="notifications")

class NotificationRead(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

# --- Analytics Models ---

class DashboardAnalytics(SQLModel):
    total_shipments: int
    pending_shipments: int
    in_transit_shipments: int
    delivered_shipments: int
    total_revenue: float
    monthly_revenue: float
    average_delivery_time: float
    customer_satisfaction: float
    top_destinations: List[dict]
    recent_shipments: List[dict]