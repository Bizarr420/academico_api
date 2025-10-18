from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

password = "Admin123!"
hash = pwd_context.hash(password)
print(f"Hash para '{password}':\n{hash}")
