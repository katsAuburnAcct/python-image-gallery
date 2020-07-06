import psycopg2
import json
import os

from gallery.ui.mySecrets import get_secret_image_gallery

# db_host = "image-gallery.c4xkuoec7dni.us-east-2.rds.amazonaws.com"
#db_name = "image_gallery"
# db_user = "image_gallery"

# Notice that this file location is not part of the git repo
# password_file = "/home/ec2-user/.image_gallery_config"

connection = None

# # returns a python dictionary
def get_secret():
    PG_HOST = os.environ.get('PG_HOST')
    IG_DATABASE = os.environ.get('IG_DATABASE')
    IG_USER = os.environ.get('IG_USER')
    IG_PASSWD = os.environ.get('IG_PASSWD')
    IG_PASSWD_FILE = os.environ.get('IG_PASSWD_FILE')

    if PG_HOST and IG_DATABASE and IG_USER and (IG_PASSWD or IG_PASSWD_FILE):
        return {
            'password' : IG_PASSWD,
            'host' : PG_HOST,
            'username': IG_USER,
            'databaseName' : IG_DATABASE
        }
    else:
        jsonString = get_secret_image_gallery()
        # converts JSON object to a python dictionary
        dict = json.loads(jsonString)
        return dict


def get_password(secret):
    if(IG_PASSWD_FILE):
       return get_password_from_file(IG_PASSWD_FILE)
    else:
        return secret['password']

def get_host(secret):
    return secret['host']

def get_username(secret):
    return secret['username']

def get_dbname(secret):
    return secret['databaseName']

def get_password_from_file():
    f = open(password_file, "r")
    result = f.readline()
    f.close()
    # remove the new line at the end of the line
    return result[:-1]

# Maintain a single connection to our db
def connect():
    global connection
    secret = get_secret()
    connection = psycopg2.connect(host=get_host(secret), dbname=get_dbname(secret), user=get_username(secret), password=get_password(secret))
#     connection = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=get_password())


#allows user to execute their query. Returns a cursor
def execute(query, args=None):
    cursor = connection.cursor()
    if not args:
        cursor.execute(query)
    else:
        cursor.execute(query, args)
    return cursor

def listUsers():
    #see all users
    res = execute('select * from users;')
    print('username\tpassword\tfull_name')
    print('-----------------------------------------')
    for row in res:
        print(row[0] + '\t\t' + row[1] + '\t\t' + row[2])

def isUsernameExist(username):
    res = execute("select count(username) from users where username=%s;", (username,))
    countRow = res.fetchone()
    return int(countRow[0]) > 0

def addUser(username, password, fullname, isadmin):
    res = execute("insert into users(username, password, full_name, isadmin) values (%s,%s,%s,%s);", (username, password, fullname, isadmin))
    connection.commit()

def editUser(username, newPassword, newFullname):
    if newPassword and newFullname:
        res = execute("update users set password=%s, full_name=%s where username=%s;", (newPassword, newFullname, username))
        connection.commit()
    elif not newPassword and newFullname:
        res = execute("update users set full_name=%s where username=%s;", (newFullname, username))
        connection.commit()
    elif newPassword and not newFullname:
        res = execute("update users set password=%s where username=%s;", (newPassword, username))
        connection.commit()
    else:
        return None

def deleteUser(username):
    res = execute("delete from users where username=%s;", (username,))
    connection.commit()

def closeConnection():
    connection.close()

def getUsers():
    res = execute('select * from users;')
    users = []
    for row in res:
        users.append(
         {
            'username': row[0],
            'fullname': row[2],
            'isadmin' : row[3]
         })
    return users

def getUser(username):
    res = execute("select * from users where username=%s;", (username,))
    user = res.fetchone()
    return {
        'username' : user[0],
        'password' : user[1],
        'fullname' : user[2],
        'isadmin' : user[3]
    }

def getUserByUserName(username):
    if(isUsernameExist(username)):
        return getUser(username)
    else:
        return None

def addImageMetadata(username, imageKey):
    res = execute("insert into images_metadata(image_owner, image_key) values (%s,%s);", (username, imageKey))
    connection.commit()

def getAllImagesByUsername(username):
    res = execute("select image_key from images_metadata where image_owner=%s;", (username, ))
    imageKeys = []
    for row in res:
        imageKeys.append(row[0])
    return imageKeys

def deleteImageMetadata(username, imagekey):
    res = execute("delete from images_metadata where image_owner=%s AND image_key=%s;", (username, imagekey))
    connection.commit()
