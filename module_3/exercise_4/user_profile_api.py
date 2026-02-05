from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Example user data (in-memory for demonstration)
users_db = {
    "1": {"id": "1", "name": "Alice", "email": "alice@example.com"},
    "2": {"id": "2", "name": "Bob", "email": "bob@example.com"}
}

class UserProfile(BaseModel):
    id: str
    name: str
    email: str

@app.get("/user/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: str):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
