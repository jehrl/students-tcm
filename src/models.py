"""Database models for students and groups."""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from datetime import datetime
import json


@dataclass
class Student:
    """Model for student data."""
    user_id: int
    email: str
    name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    active: bool = True
    newsletter: bool = False
    internal_note: Optional[str] = None
    active_to: Optional[datetime] = None
    
    # Address fields
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None
    address_phone: Optional[str] = None
    
    # Relationships
    group_ids: Set[int] = field(default_factory=set)
    
    def __post_init__(self):
        """Validate and clean data after initialization."""
        if self.email:
            self.email = self.email.strip().lower()
        if self.name:
            self.name = self.name.strip()
        if self.surname:
            self.surname = self.surname.strip()
    
    @property
    def full_name(self) -> str:
        """Get full name of the student."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.name:
            parts.append(self.name)
        if self.surname:
            parts.append(self.surname)
        return " ".join(parts)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'title': self.title,
            'name': self.name,
            'surname': self.surname,
            'full_name': self.full_name,
            'active': self.active,
            'newsletter': self.newsletter,
            'internal_note': self.internal_note,
            'active_to': self.active_to.isoformat() if self.active_to else None,
            'address_street': self.address_street,
            'address_city': self.address_city,
            'address_zip': self.address_zip,
            'address_country': self.address_country,
            'address_phone': self.address_phone,
            'group_ids': list(self.group_ids)
        }


@dataclass
class Group:
    """Model for group/course data."""
    group_id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    year: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    student_ids: Set[int] = field(default_factory=set)
    
    def __post_init__(self):
        """Process group name to extract metadata."""
        if self.name:
            self.name = self.name.strip()
            self._extract_metadata()
    
    def _extract_metadata(self):
        """Extract metadata from group name."""
        name_upper = self.name.upper()
        
        # Determine category
        if 'LEKTOŘI' in name_upper or 'LEKTOR' in name_upper:
            self.category = 'LEKTOŘI'
        elif 'STUDIUM' in name_upper:
            self.category = 'STUDIUM'
        elif 'SEMINÁŘ' in name_upper:
            self.category = 'SEMINÁŘ'
        elif 'ADMIN' in name_upper:
            self.category = 'ADMIN'
        elif 'ČLEN' in name_upper or 'ČLENOVÉ' in name_upper:
            self.category = 'ČLENOVÉ'
        else:
            self.category = 'KURZ'
        
        # Extract year if present
        import re
        year_patterns = [
            r'(\d{4})-(\d{4})',  # e.g., 2023-2024
            r'(\d{4})',           # e.g., 2023
        ]
        for pattern in year_patterns:
            match = re.search(pattern, self.name)
            if match:
                self.year = match.group(0)
                break
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'year': self.year,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'student_count': len(self.student_ids),
            'student_ids': list(self.student_ids)
        }


@dataclass
class StudentGroup:
    """Model for student-group relationship."""
    student_id: int
    group_id: int
    enrolled_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'student_id': self.student_id,
            'group_id': self.group_id,
            'enrolled_at': self.enrolled_at.isoformat()
        }