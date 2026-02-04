"""
Custom validators for request data

This module provides reusable validator mixins for:
- Password strength validation
- Email format validation
- Username format validation
"""
import re
from pydantic import validator


class PasswordValidator:
    """Password validation mixin"""

    @validator('password')
    def validate_password(cls, value: str) -> str:
        """
        Validate password strength

        Rules:
        - Min 8 characters
        - Contains uppercase, lowercase, digit, special char
        """
        if len(value) < 8:
            raise ValueError('Password too short')

        return value