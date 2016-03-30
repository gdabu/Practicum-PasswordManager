import bcrypt

plaintextPassword = "test".encode('utf-8')
hashedPassword = bcrypt.hashpw(plaintextPassword, bcrypt.gensalt())


password = "test".encode('utf-8')

bitch = ("$2b$12$TM4dW9uM6e8WmF1VdhI8HOFYpmeRehykS6b/cXfVM4.zj3ztBQcLi" == bcrypt.hashpw(plaintextPassword, "$2b$12$TM4dW9uM6e8WmF1VdhI8HOFYpmeRehykS6b/cXfVM4.zj3ztBQcLi"))
print bitch
# $2a$10$llw0G6IyibUob8h5XRt9xuRczaGdCm/AiV6SSjf5v78XS824EGbh.