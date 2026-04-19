from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"


class ClientRoleType(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    LANDLORD = "landlord"
    TENANT = "tenant"
    INVESTOR = "investor"
    GENERAL_LEAD = "general_lead"


class ClientStatus(str, Enum):
    NEW = "new"
    ACTIVE = "active"
    QUALIFIED = "qualified"
    NURTURING = "nurturing"
    INACTIVE = "inactive"
    CLOSED = "closed"


class ListingType(str, Enum):
    SALE = "sale"
    RENT = "rent"


class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    OFFICE = "office"
    LAND = "land"
    OTHER = "other"


class PropertyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RESERVED = "reserved"
    SOLD = "sold"
    RENTED = "rented"
    ARCHIVED = "archived"


class DealType(str, Enum):
    SALE = "sale"
    RENT = "rent"


class DealStage(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    VIEWING = "viewing"
    OFFER = "offer"
    NEGOTIATION = "negotiation"
    CONTRACT = "contract"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class DealStatus(str, Enum):
    OPEN = "open"
    ON_HOLD = "on_hold"
    WON = "won"
    LOST = "lost"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InteractionType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    VIEWING = "viewing"
    NOTE = "note"
    MESSAGE = "message"


class RelatedEntityType(str, Enum):
    CLIENT = "client"
    PROPERTY = "property"
    DEAL = "deal"
    GENERAL = "general"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    EXPORT = "export"
    IMPORT = "import"
    BACKUP = "backup"
