import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt

import sqlalchemy.orm as _orm
import passlib.hash as _hash

import database as _database, models as _models, schemas as _schemas

oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "myjwtsecret"


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(db: _orm.Session, email: str):
    return db.query(_models.User).filter(_models.User.email == email).first()


async def create_user(db: _orm.Session, user: _schemas.UserCreate):
    new_user = _models.User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def authenticate_user(db: _orm.Session, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):
    user_object = _schemas.User.from_orm(user)

    token = _jwt.encode(user_object.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db), token: str = _fastapi.Depends(oauth2_scheme)
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except _jwt.PyJWTError:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid email or password"
        )

    return _schemas.User.from_orm(user)
