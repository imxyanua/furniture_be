from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserCreate, LoginRequest, Token
from ..models.user import User
from ..utils.security import create_access_token  # ONLY this!
from ..utils.helpers import generate_id
from datetime import timedelta
from ..config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"📝 REGISTER - Phone: {user_data.phone}, Email: {user_data.email}")
        
        if not user_data.email and not user_data.phone:
            raise HTTPException(status_code=400, detail="Email or phone required")
        
        if user_data.email and db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if user_data.phone and db.query(User).filter(User.phone == user_data.phone).first():
            raise HTTPException(status_code=400, detail="Phone already registered")
        
        new_user = User(
            id=generate_id("USR"),
            email=user_data.email,
            phone=user_data.phone,
            password_hash=user_data.password,  # Plain text
            full_name=user_data.full_name,
            role=getattr(user_data, 'role', 'user')
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ REGISTER SUCCESS - {new_user.id}")
        
        access_token = create_access_token(
            data={
                "sub": new_user.id,
                "role": new_user.role,
                "email": new_user.email or new_user.phone
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ REGISTER ERROR: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"🔐 LOGIN - Phone: {login_data.phone}, Email: {login_data.email}")
        
        if not login_data.email and not login_data.phone:
            raise HTTPException(status_code=400, detail="Email or phone required")
        
        user = None
        
        if login_data.email:
            user = db.query(User).filter(User.email == login_data.email).first()
            
        elif login_data.phone:
            phone = login_data.phone.strip().replace(' ', '').replace('-', '')
            
            # Try multiple formats
            phone_formats = [phone]
            if phone.startswith('+84'):
                phone_formats.append('0' + phone[3:])
            elif phone.startswith('84') and not phone.startswith('0'):
                phone_formats.append('0' + phone[2:])
            elif phone.startswith('0'):
                phone_formats.append(phone[1:])
            
            for fmt in phone_formats:
                user = db.query(User).filter(User.phone == fmt).first()
                if user:
                    break
        
        if not user:
            logger.warning(f"❌ USER NOT FOUND")
            raise HTTPException(status_code=401, detail="Incorrect credentials")
        
        if user.status != 'active':
            raise HTTPException(status_code=403, detail=f"Account is {user.status}")
        
        # ✅ PLAIN TEXT COMPARISON
        if login_data.password != user.password_hash:
            logger.warning(f"❌ WRONG PASSWORD")
            raise HTTPException(status_code=401, detail="Incorrect credentials")
        
        logger.info(f"✅ LOGIN SUCCESS - {user.id} (role: {user.role})")
        
        access_token = create_access_token(
            data={
                "sub": user.id,
                "role": user.role,
                "email": user.email or user.phone
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ LOGIN ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))