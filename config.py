"""
Application configuration and constants.
"""
import os
from enum import Enum
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / 'data'
DESIGN_DIR = BASE_DIR / 'design'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
DESIGN_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Data files
CLIENTS_CSV = DATA_DIR / 'clients.csv'
HOME_VALUE_CSV = DATA_DIR / 'home_value.csv'
DEALS_CSV = DATA_DIR / 'deal_pipeline.csv'
DEAL_FIXTURE = DATA_DIR / 'deal_pipeline_fixture.csv'

# CSV Schemas
CLIENT_COLUMNS = [
    "id", "name", "email", "phone", "preferred_contact",
    "timeline", "address", "source", "tags", "optin_email",
    "optin_sms", "status", "notes"
]

DEAL_COLUMNS = [
    'id', 'name', 'stage', 'ticket_size', 'local_partner',
    'country', 'expected_close', 'risk_score', 'tags', 'notes'
]


class ContactMethod(str, Enum):
    """Preferred contact methods."""
    PHONE = "Phone"
    EMAIL = "Email"
    TEXT = "Text"


class Timeline(str, Enum):
    """Client timeline options."""
    ZERO_TO_THREE = "0-3 months"
    THREE_TO_SIX = "3-6 months"
    SIX_TO_TWELVE = "6-12 months"
    TWELVE_PLUS = "12+ months"
    BROWSING = "Just browsing"


class LeadSource(str, Enum):
    """Lead source options."""
    WEBSITE = "Website"
    YOUTUBE = "YouTube"
    REFERRAL = "Referral"
    SOCIAL = "Social"
    OTHER = "Other"


class ClientStatus(str, Enum):
    """Client status options."""
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    ACTIVE = "Active"
    CLOSED = "Closed"
    LOST = "Lost"


class DealStage(str, Enum):
    """Deal pipeline stages."""
    NEW = "New"
    SOURCED = "Sourced"
    SCREENING = "Screening"
    TERM_SHEET = "Term Sheet"
    DUE_DILIGENCE = "Due Diligence"
    CLOSED_WON = "Closed-Won"
    CLOSED_LOST = "Closed-Lost"


# Application settings
APP_TITLE = "Goodman-Taylor Studio"
APP_SUBTITLE = "Real Estate + Interior Design Dashboard"
COMPANY_MISSION = (
    "We love pets, support families, and champion active living — "
    "design and real-estate solutions built for everyday life."
)
COMPANY_VALUES = "Family-first · Pet-friendly · Active-lifestyle"
COMPANY_TAGLINE = "I like my dog, I like helping families, and I like being active."

# Security
ADMIN_PASS = os.getenv("ADMIN_PASS")

# File upload settings
ALLOWED_IMAGE_TYPES = ["jpg", "png", "jpeg"]
MAX_UPLOAD_SIZE_MB = 10
