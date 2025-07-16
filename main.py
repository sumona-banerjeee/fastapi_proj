from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict

app = FastAPI()

# Simulated "database" of users and their roles
fake_users_db = {
    "alice-token": {"username": "alice", "role": "admin"},
    "bob-token": {"username": "bob", "role": "user"},
    "carol-token": {"username": "carol", "role": "editor"},
    "john-token": {"username": "john", "role": "viewer"}
}

# Use API Key authentication via headers
api_key_header = APIKeyHeader(name="Authorization")


def get_current_user(api_key: str = Security(api_key_header)):
    """
    Dependency that gets the current user based on the API token.
    """
    user = fake_users_db.get(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    return user


def require_role(required_role: str):
    """
    Factory function to create dependencies that enforce role-based access.
    """
    def role_checker(user: Dict = Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role '{required_role}'"
            )
        return user
    return role_checker

# Serve static files from "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at "/"
@app.get("/", response_class=FileResponse)
def root():
    return FileResponse("static/index.html")


@app.get("/protected")
def protected_endpoint(user: Dict = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}, you are authenticated as {user['role']}."}


@app.get("/admin-only")
def admin_endpoint(user: Dict = Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user['username']}!"}


@app.get("/editor-only")
def editor_endpoint(user: Dict = Depends(require_role("editor"))):
    return {"message": f"Welcome editor {user['username']}!"}


@app.get("/viewer-only")
def viewer_endpoint(user: Dict = Depends(require_role("viewer"))):
    return {"message": f"Hello viewer {user['username']}"}
