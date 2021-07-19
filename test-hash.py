from werkzeug.security import check_password_hash, generate_password_hash
from sys import argv

hashed = generate_password_hash(argv[1])
print(f"Your hashed password is {hashed}")
