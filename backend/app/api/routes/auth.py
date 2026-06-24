from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    # HOTFIX: Pastikan kolom jenis_kelamin ada di DB sebelum query
    from sqlalchemy import text
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS jenis_kelamin VARCHAR(20)"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Hotfix migration skip/fail (likely already exists): {e}")

    try:
        # Cek email sudah ada
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email sudah digunakan"
            )
        
        user = User(
            nama=data.nama,
            email=data.email,
            password=hash_password(data.password),
            jenis_kelamin=data.jenis_kelamin
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Registrasi berhasil", "id_user": str(user.id_user)}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"ERROR SAAT REGISTRASI: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan di server: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password tidak valid"
        )
    
    token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return TokenResponse(
        access_token=token,
        user={
            "id_user": str(user.id_user),
            "nama": user.nama,
            "email": user.email,
            "role": user.role
        }
    )
