import pyotp
import time
import datetime

# totp = pyotp.TOTP(pyotp.random_base32())
# secret = totp.at(datetime.datetime.now()) # => 492039
# print secret

# count = 0

# while True:
# 	# OTP verified for current time
# 	print totp.verify(secret) # => True
# 	time.sleep(1)
# 	count = count + 1
# 	print count 
# 	
geoff = pyotp.random_base32()
hotp = pyotp.HOTP(pyotp.random_base32())

counter = 1
secret = hotp.at(counter) # => 316439

while True:
	# OTP verified with a counter
	print hotp.verify(secret, counter) # => True
	time.sleep(1)