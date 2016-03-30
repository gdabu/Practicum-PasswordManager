import bcrypt

password = "test".encode('utf-8')

bitch = (bcrypt.hashpw(password, "$2b$12$TM4dW9uM6e8WmF1VdhI8HOFYpmeRehykS6b/cXfVM4.zj3ztBQcLi") == password)
print bitch
# $2a$10$llw0G6IyibUob8h5XRt9xuRczaGdCm/AiV6SSjf5v78XS824EGbh.