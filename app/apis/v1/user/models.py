"""Request module for user API."""

from pydantic import BaseModel, EmailStr, Field, constr


class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""

    name: constr(min_length=1, max_length=50) = Field(  # type: ignore
        ...,
        description="The name of the user. Must be between 1 and 50 characters.",
        example="John Doe",
    )
    logo: str = Field(  # type: ignore
        ...,
        description="URL to the user's logo or profile picture.",
        example="https://example.com/logo.png",
    )
    email: EmailStr = Field(  # type: ignore
        ...,
        description="Valid email address of the user.",
        example="johndoe@example.com",
    )
    password: constr(min_length=8) = Field(  # type: ignore
        ...,
        description="Password for the user. Must be at least 8 characters long.",
        example="P@ssw0rd!",
    )
