from fastapi import APIRouter, Depends, status, HTTPException, Response
from .. import oauth2, utils, schemas
from core import models, database
from sqlalchemy.orm import Session
from sqlalchemy import or_

logger = logging.getLogger(__name__)  # to make logs 

router = APIRouter(
    tags=['Authentication']
)


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: schemas.UserLogin, 
    db: Session=Depends(database.get_db)
):
    """
    Handles user authentication.
    """
    # Query user by email or username
    user_email_query = db.query(models.User).filter(
        or_(
            models.User.email == user_credentials.identifier,
            models.User.username == user_credentials.identifier
        )
    )
    user = user_email_query.first()

    # Account does not exist
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f'Invalid Credentials')
    # Password verification
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f'Invalid Credentials')

    # Create JWT access token
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
