"""
Data models and validation for the application.
"""
import re
from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid


@dataclass
class ClientRecord:
    """Client/lead record with validation."""
    name: str
    email: str = ""
    phone: str = ""
    preferred_contact: str = "Email"
    timeline: str = "Just browsing"
    address: str = ""
    source: str = "Website"
    tags: str = ""
    optin_email: bool = False
    optin_sms: bool = False
    status: str = "New"
    notes: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Client name is required")
        
        self.email = self.email.strip()
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email address: {self.email}")
        
        self.phone = self._normalize_phone(self.phone)
        self.address = self.address.strip()
        self.notes = self.notes.strip()
        
        # Normalize tags
        if self.tags:
            tags_list = [t.strip() for t in self.tags.split(",") if t.strip()]
            self.tags = ",".join(tags_list)
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize phone number to digits only."""
        if not phone:
            return ""
        return re.sub(r'[^\d+]', '', phone)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export."""
        return asdict(self)


@dataclass
class DealRecord:
    """Deal pipeline record with validation."""
    name: str
    stage: str = "New"
    ticket_size: int = 0
    local_partner: str = ""
    country: str = ""
    expected_close: str = ""
    risk_score: int = 5
    tags: str = ""
    notes: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Deal name is required")
        
        if self.risk_score < 1 or self.risk_score > 10:
            raise ValueError("Risk score must be between 1 and 10")
        
        if self.ticket_size < 0:
            raise ValueError("Ticket size cannot be negative")
        
        self.local_partner = self.local_partner.strip()
        self.country = self.country.strip()
        self.notes = self.notes.strip()
        
        # Normalize tags
        if self.tags:
            tags_list = [t.strip() for t in self.tags.split(",") if t.strip()]
            self.tags = ",".join(tags_list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export."""
        data = asdict(self)
        # Ensure ticket_size and risk_score are strings for CSV consistency
        data['ticket_size'] = str(data['ticket_size'])
        data['risk_score'] = str(data['risk_score'])
        return data
