from twisted.enterprise import adbapi
from twisted.internet import reactor

dbpool = adbapi.ConnectionPool("MySQLdb", user="root", passwd="bastard11", db="pwd_manager", host="Localhost")


# equivalent of cursor.execute(statement), return cursor.fetchall():

def readUserPasswords(user):
    return dbpool.runQuery("select * from password where username = '" + user + "'")

def createUserPassword(user, account, password):
    return dbpool.runQuery("insert into passwords (username, account, password) values ('" + user + "', '" + account + "', '" + password + "')" )

def deleteUserPassword(user, passwordId):
    return dbpool.runQuery("delete from passwords where id = " + passwordId + " and username = '" + user + "'")

def updateUserPassword(user, passwordId, column, newValue):
    return dbpool.runQuery("update passwords set " + column + "='" + newValue + "' where id = " + passwordId + " and username = '" + user + "'")

def createUser(newUser, newPassword):
    return dbpool.runQuery("insert into users (username, password) values ('" + newUser + "', '" + newPassword + "')")

def printResult(l):
    print l

readUserPasswords("test@test.com").addCallback(printResult)
reactor.run()