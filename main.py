import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm

import services as _services, schemas as _schemas
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = _fastapi.FastAPI()
handler = Mangum(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello():
    return {"message": "Hello World"}


@app.post("/api/users")
async def create_user(
    user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(db, user.email)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already registered")

    user = await _services.create_user(db, user)

    return await _services.create_token(user)


@app.post("/api/token")
async def generate_token(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
):
    user = await _services.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid email or password"
        )

    return await _services.create_token(user)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.get("/api")
async def root():
    return {"message": "Banks Reports"}
