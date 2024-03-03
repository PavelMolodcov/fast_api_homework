from pydantic import BaseModel, field_validator, EmailStr, SecretStr
from pydantic_core import PydanticCustomError
from email_validator import validate_email, EmailNotValidError
from .books import ReturnedBookForSeller


__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "ReturnedSellerWithBooks"]

# Базовый класс продавца
class BaseSeller(BaseModel):
    
    first_name: str
    last_name: str
    
    

class IncomingSeller(BaseSeller): 
    
    email: EmailStr
    password: SecretStr

    @field_validator("email")
    @staticmethod
    def validate_email(val: EmailStr):
        try:
            validate_email(val)
            return val
        except EmailNotValidError as e:
            raise PydanticCustomError(str(e), 'email not valid') from e
        

class ReturnedSeller(BaseSeller):
    id: int
    email: EmailStr
    

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBookForSeller]