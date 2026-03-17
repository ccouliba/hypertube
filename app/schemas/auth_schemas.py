"""Auth domain Marshmallow schemas — validation + serialisation"""
import re
from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    ValidationError,
    post_load,
    EXCLUDE,
)
from app.core.configs import AUTH_CONFIG

_pw: dict = AUTH_CONFIG["password"]
_usr: dict = AUTH_CONFIG["username"]
_supported_languages: list[str] = AUTH_CONFIG["supported_languages"]


class RegisterSchema(Schema):
    """Validate user registration payload"""

    class Meta:
        unknown = EXCLUDE

    firstname = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=80),
    )
    lastname = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=80),
    )
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=_usr["min_length"],
                max=_usr["max_length"],
                error=f"Username must be between {_usr['min_length']} and {_usr['max_length']} characters",
            ),
            validate.Regexp(
                _usr["authorized_characters"],
                error="Username can only contain letters, numbers, _ and -",
            ),
        ],
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(
            min=_pw["min_length"],
            error=f"Password must be at least {_pw['min_length']} characters",
        ),
    )

    @validates("password")
    def validate_password_strength(self, value: str) -> None:
        if not re.search(r"[A-Za-z]", value):
            raise ValidationError("Password must contain at least one letter")
        if not re.search(r"\d", value):
            raise ValidationError("Password must contain at least one digit")
        if not re.search(_pw["special_characters"], value):
            raise ValidationError(
                'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
            )

    @post_load
    def clean(self, data: dict, **kwargs) -> dict:
        data["firstname"] = data["firstname"].strip()
        data["lastname"] = data["lastname"].strip()
        data["username"] = data["username"].strip()
        data["email"] = data["email"].strip().lower()
        return data


class LoginSchema(Schema):
    """Validate login payload"""

    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=1))

    @post_load
    def clean(self, data: dict, **kwargs) -> dict:
        data["username"] = data["username"].strip()
        return data


class UpdateUserSchema(Schema):
    """Validate partial user update payload (all fields optional)"""

    class Meta:
        unknown = EXCLUDE

    firstname = fields.Str(validate=validate.Length(min=1, max=80))
    lastname = fields.Str(validate=validate.Length(min=1, max=80))
    username = fields.Str(
        validate=[
            validate.Length(
                min=_usr["min_length"],
                max=_usr["max_length"]
            ),
            validate.Regexp(
                _usr["authorized_characters"],
                error="Username can only contain letters, numbers, _ and -",
            ),
        ]
    )
    email = fields.Email()
    language = fields.Str(
        validate=validate.OneOf(
            _supported_languages,
            error=f"Supported languages: {', '.join(_supported_languages)}",
        )
    )
    profile_picture = fields.Str(validate=validate.Length(min=1))

    @post_load
    def clean(self, data: dict, **kwargs) -> dict:
        return {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
            if v is not None and v != ""
        }


# Output schemas

class UserPublicSchema(Schema):
    """Full user representation for authenticated responses"""
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()
    firstname = fields.Str()
    lastname = fields.Str()
    language = fields.Str()
    profile_picture = fields.Str()


class UserMiniSchema(Schema):
    """Minimal user representation for lists"""
    id = fields.Int()
    username = fields.Str()


class LoginResponseSchema(Schema):
    message = fields.Str()
    access_token = fields.Str()
    user = fields.Nested(UserPublicSchema)


class AccessTokenResponseSchema(Schema):
    """Response body for /refresh"""
    access_token = fields.Str()
    user = fields.Nested(UserPublicSchema)


class RegisterResponseSchema(Schema):
    message = fields.Str()
    user = fields.Dict()  # { username, profile_picture }


class UpdateUserResponseSchema(Schema):
    message = fields.Str()
    user = fields.Nested(UserPublicSchema)


class UsersListResponseSchema(Schema):
    users = fields.List(fields.Nested(UserMiniSchema))


class MessageSchema(Schema):
    message = fields.Str()
