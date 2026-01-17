from .. import schemas, utils
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from core.database import get_db
from core import models
from sqlalchemy import or_
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags = ['Users']
)

# USER crud operations
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user_credentials: schemas.UserCreate, db: Session=Depends(get_db)):
    """
    User Creation:
    - Handles the creation of new user accounts.
    - Ensures that `email` and `username` are unique checks the database.
    """
    # Check in the database
    existing_user = db.query(models.User).filter(
        or_(
            models.User.email == user_credentials.email,
            models.User.username == user_credentials.username
        )
    ).first()

    if existing_user:
        # Check which field already exists for a better error message
        if existing_user.email == user_credentials.email:
            detail = "Email already registered"
        else:
            detail = "Username already registered"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=detail)

    # Hash the password
    hashed_password = utils.hash(user_credentials.password)
    user_credentials.password = hashed_password

    # Create the new user from the input credentials
    new_user = models.User(**user_credentials.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session=Depends(get_db)):
    """
    Fetch user details by user_id.
    """
    user_search_query = db.query(models.User).filter(models.User.id == id)
    user = user_search_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not found")

    return user
    