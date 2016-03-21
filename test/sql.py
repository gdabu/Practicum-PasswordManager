import MySQLdb

db = MySQLdb.connect(host="localhost", user="root", passwd="bastard11", db="pwd_manager")
cursor = db.cursor()

try: 
	cursor.execute("insert into users (username, password) values ('test1', 'password1')")


except Exception, e:
	print e[0]