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

def PasswordCreate(db, username, account, password):
    cursor = db.cursor()
    cursor.execute("insert into passwords (username, account, password) values ('" + username + "', '" + account + "', '" + password + "')" )
    db.commit()