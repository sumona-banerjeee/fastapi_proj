from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, Dict
from datetime import datetime, timedelta

app = FastAPI()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "yoursecretkey"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {}


app.mount("/static", StaticFiles(directory="static"), name="static")



def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return fake_users_db[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse("static/index.html")


@app.get("/signup", response_class=FileResponse)
def signup_page():
    return FileResponse("static/signup.html")


@app.get("/login", response_class=FileResponse)
def login_page():
    return FileResponse("static/login.html")


@app.get("/welcome", response_class=FileResponse)
def welcome_page(user: dict = Depends(get_current_user)):
    return FileResponse("static/welcome.html")



@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {"username": username, "hashed_password": hashed_password, "role": role}
    return RedirectResponse(url="/login", status_code=303)



@app.post("/login")
async def login(response: HTMLResponse, username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": username})
    resp = RedirectResponse(url="/welcome", status_code=303)
    resp.set_cookie(key="access_token", value=access_token, httponly=True)
    return resp


@app.get("/admin-data")
def read_admin_data(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": f"Hello {user['username']}, you are an admin!"}


@app.get("/user-data")
def read_user_data(user: dict = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}, your role is {user['role']}."}
