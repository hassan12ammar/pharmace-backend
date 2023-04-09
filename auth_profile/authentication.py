# import libraries
from jose import jwt, JWTError
from ninja.security import HttpBearer
# import files
from basbos.settings import SECRET_KEY


# customizing the HttpBearer class
class CustomAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=["HS256"]
            )
            username = payload.get("username")
        except JWTError:
            return None
        if username is None:
            return None
        return str(username)


# generate token for the user
def create_token(user):
    payload = {"username": str(user.email)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"access": str(token)}


