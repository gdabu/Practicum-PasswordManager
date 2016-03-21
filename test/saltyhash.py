import bcrypt

plaintext_password = "fuck head"
password_attempt = "fuck heads"
hashed = bcrypt.hashpw(plaintext_password, bcrypt.gensalt())
print hashed

if bcrypt.hashpw(password_attempt, hashed) == hashed:
    print "It matches"
else:
    print "It does not match"