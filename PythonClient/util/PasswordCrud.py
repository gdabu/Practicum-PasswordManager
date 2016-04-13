import json

def PasswordRead(db, username):
    cursor = db.cursor()
    cursor.execute("select * from passwords where username = '" + username + "'" )
    passwords = cursor.fetchall()

    passwordList = []

    for row in passwords:
        passwordList.append({ 
            "id" : row[0],
            "username" :  row[1],
            "account" :  row[2],
            "password" :  row[3]
        })

    db.commit()

    return passwordList

def PasswordDelete(db, username, passwordId):
    cursor = db.cursor()
    cursor.execute("delete from passwords where id = " + `passwordId` + " and username = '" + username + "'")
    db.commit()

def PasswordDeleteAll(db, username):
    cursor = db.cursor()
    cursor.execute("delete from passwords where username='" + username + "'")
    db.commit()

def PasswordCreate(db, username, account, password):
    cursor = db.cursor()
    cursor.execute("insert into passwords (username, account, password) values ('" + username + "', '" + account + "', '" + password + "')" )
    db.commit()

def PasswordsCreate(db, username, passwordList):
    cursor = db.cursor()
    for password in passwordList:
        cursor.execute("insert into passwords (username, account, password) values ('" + username + "', '" + password['account'] + "', '" + password['password'] + "')" )
    db.commit()

def PasswordUpdate(db, username, column, newValue, passwordId):
    cursor.execute("update passwords set " + column + "='" + newValue + "' where id = " + `passwordId` + " and username = '" + username + "'")

def UserCreate(db, username, password):
    cursor = db.cursor()
    cursor.execute("insert into users (username, password) values ('" + username + "', '" + password + "')")
    db.commit()

def GetUser(db, username):
    cursor = db.cursor()
    cursor.execute("select * from users where username = '" + username + "'")

    user = cursor.fetchall()
    db.commit()

    return user

