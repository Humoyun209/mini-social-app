import bcrypt

passwords = {
    "alice": "password123",
    "bob": "password123",
    "charlie": "password123",
    "diana": "password123",
    "eve": "password123",
    "frank": "password123",
}

print("UPDATE users SET password_hash = CASE username")
for username, password in passwords.items():
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    hash_str = hashed.decode("utf-8")
    print(f"    WHEN '{username}' THEN '{hash_str}'")
print("END;")
