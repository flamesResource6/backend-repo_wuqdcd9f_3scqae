"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- Lead -> "lead" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Lead(BaseModel):
    """
    Client leads captured from service/contact forms
    Collection: "lead"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    description: str = Field(..., description="Idea / requirement description")
    branding: Optional[str] = Field('No', description="Whether client has branding (Yes/No)")
    service: Optional[str] = Field(None, description="Service interest (if from Services)")
