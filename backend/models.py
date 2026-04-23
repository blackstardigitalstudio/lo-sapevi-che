"""Pydantic request models for Lo Sapevi che? backend."""
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    interests: List[str] = Field(default_factory=list)
    security_question: str = Field(min_length=3, max_length=200)
    security_answer: str = Field(min_length=1, max_length=200)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotQuestionIn(BaseModel):
    email: EmailStr


class ForgotResetIn(BaseModel):
    email: EmailStr
    security_answer: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=6)


class SetSecurityQuestionIn(BaseModel):
    security_question: str = Field(min_length=3, max_length=200)
    security_answer: str = Field(min_length=1, max_length=200)
    current_password: str = Field(min_length=1)


class SetLanguageIn(BaseModel):
    language: str = Field(pattern="^(it|en|es)$")


class UpdateInterestsIn(BaseModel):
    interests: List[str]


class UpdateSubInterestsIn(BaseModel):
    sub_interests: Dict[str, List[str]]


class ReactIn(BaseModel):
    action: str  # "like" | "dislike"


class PushTokenIn(BaseModel):
    token: str


class GenerateIn(BaseModel):
    category: Optional[str] = None


class BulkGenerateIn(BaseModel):
    count: int = Field(default=5, ge=1, le=10)
    category: Optional[str] = None
