from ninja import Schema
from typing import Optional
from pydantic import EmailStr, Field
from phonenumber_field.formfields import PhoneNumberField


# General Schemas
class MessageOut(Schema):
    detail: str


# Authentication Schemas
class UserIn(Schema):
    email: EmailStr
    password1: str = Field(min_length=8)
    password2: str = Field(min_length=8)


class TokenOut(Schema):
    access: str


class UserOut(Schema):
    email: EmailStr


class AuthOut(Schema):
    token: TokenOut
    user: UserOut


class SigninIn(Schema):
    email: EmailStr
    password: str

# Profile Schemas

class ProfileSchema(Schema):
    name: str
    img: Optional[str] = None
    phone_number: Optional[str]


class ProfileIn(ProfileSchema):
    city: str
    state: str



class ProfileOut(ProfileSchema):
    address: str
    email: EmailStr


class ProfileSchemaUpdate(ProfileIn):
    pass


class ProfileDelete(Schema):
    pass
