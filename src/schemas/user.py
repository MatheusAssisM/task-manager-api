from pydantic import BaseModel, EmailStr, field_validator, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str


class UserRegisterResponse(BaseModel):
    message: str = "User registered successfully"
    user: UserResponse


class UserLoginResponse(BaseModel):
    access_token: str
    expires_in: int
    user: UserResponse


class UserLogoutResponse(BaseModel):
    message: str = "Successfully logged out"


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetRequestResponse(BaseModel):
    message: str = (
        "If an account exists with this email, you will receive password reset instructions."
    )


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class PasswordResetResponse(BaseModel):
    message: str = "Password successfully reset"
