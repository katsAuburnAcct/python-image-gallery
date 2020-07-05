import sys
sys.path.append('/home/ec2-user/python-image-gallery/gallery/ui')

from flask import Flask, request, render_template, session, redirect, send_file
from gallery.ui.db import getUsers, addUser, editUser, deleteUser, getUserByUserName, connect, addImageMetadata, getAllImagesByUsername, deleteImageMetadata
from gallery.ui.session_secrets import get_secret_flask_session
from gallery.ui.uploadFile import upload_file, download_file, delete_object
from functools import wraps

import json, os

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY')
print('SESSION_SECRET_KEY')
print(SESSION_SECRET_KEY)
if SESSION_SECRET_KEY:
    app.secret_key = SESSION_SECRET_KEY
    print('SESSION_SECRET_KEY if statement executed')
else:
    jsonString = get_secret_flask_session()
    dict = json.loads(jsonString)
    app.secret_key = dict['secret_key']

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


connect()

def getIsAuthenticated():
    return 'username' in session

def requiresAuthenticated(view):
    @wraps(view)
    def decorated(**kwargs):
        if not getIsAuthenticated():
            return redirect('/login')
        else:
            return view(**kwargs)
    return decorated

def getIsAdmin():
    user = getUserByUserName(session['username'])
    return 'username' in session and user.get('isadmin')

def requiresAdmin(view):
    @wraps(view)
    def decorated(**kwargs):
        if not getIsAdmin():
            return redirect('/login')
        else:
            return view(**kwargs)
    return decorated


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/invalid-login')
def invalidLogin():
    return render_template('invalidLogin.html')

@app.route('/admin')
@requiresAuthenticated
@requiresAdmin
def admin():
    users = getUsers()
    return render_template('admin.html', users= users)

@app.route('/admin/create')
@requiresAuthenticated
@requiresAdmin
def createUserRoute():
    return render_template('createUser.html')

@app.route('/admin/edit/<username>')
@requiresAuthenticated
@requiresAdmin
def editUserRoute(username):
    return render_template('editUser.html', username= username)

@app.route('/admin/delete/<username>')
@requiresAuthenticated
@requiresAdmin
def deleteUserRoute(username):
    return render_template('deleteUser.html', username= username)

@app.route('/')
@requiresAuthenticated
def mainMenuRoute():
    return render_template('mainMenu.html')


@app.route('/create-user', methods=['POST'])
@requiresAuthenticated
@requiresAdmin
def onCreateUser():
    if request.method == 'POST':
        requestDict = request.form.to_dict()
        isadmin = requestDict.get('isadmin').rstrip()
        isadminFormatted = False
        if isadmin == 'true':
            isadminFormatted = True

        addUser(requestDict.get('username').rstrip(), requestDict.get('password').rstrip(), requestDict.get('fullName').rstrip(), isadminFormatted)
    users = getUsers()
    return render_template('admin.html', users= users)

@app.route('/edit-user', methods=['POST'])
@requiresAuthenticated
@requiresAdmin
def onEditUser():
    if request.method == 'POST':
        requestDict = request.form.to_dict()
        editUser(requestDict.get('username').rstrip(), requestDict.get('password').rstrip(), requestDict.get('fullName').rstrip())
    users = getUsers()
    return render_template('admin.html', users= users)

@app.route('/delete-user/<username>')
@requiresAuthenticated
@requiresAdmin
def onDeleteUser(username):
    deleteUser(username.rstrip())
    users = getUsers()
    return render_template('admin.html', users= users)

@app.route('/login-user', methods=['POST'])
def onLoginUser():
    if request.method == 'POST':
        requestDict = request.form.to_dict()
        myPass = requestDict.get("pass").rstrip()
        user = getUserByUserName(requestDict.get("username").rstrip())
        if user is None or user.get('password') != myPass:
            return redirect('/invalid-login')
        else:
            # Store username to session data
            session['username'] = requestDict.get("username")
            return redirect('/')

@app.route('/upload')
@requiresAuthenticated
def upload():
    return render_template('upload.html')



@app.route('/upload-image', methods=['POST'])
@requiresAuthenticated
def onUpload():
    f = request.files['file']
    print(f)
    f.save(os.path.join(UPLOAD_FOLDER, f.filename))
    upload_file(f"{UPLOAD_FOLDER}/{f.filename}")

    addImageMetadata(session['username'], f.filename)

    return redirect("/")


def getImages():
    images = []
    imageKeys = getAllImagesByUsername(session['username'])
    for imageKey in imageKeys:
        download_file(imageKey)
        images.append({
            'filepath': "downloads/" + imageKey,
            'imagekey': imageKey
        })
    return images

@app.route('/view', methods=['GET', 'POST'])
@requiresAuthenticated
def view():
    images = getImages()
    return render_template('view.html', username=session['username'], images=images)

@app.route('/downloads/<filename>')
@requiresAuthenticated
def serveImage(filename):
    return send_file('downloads/' + filename, mimetype='image/jpeg')

@app.route('/delete-image/<imagekey>')
@requiresAuthenticated
def deleteImage(imagekey):
    return render_template('delete_image.html', imagekey=imagekey)

@app.route('/on-delete-image/<imagekey>')
@requiresAuthenticated
def onDeleteImage(imagekey):
    # delete from s3 bucket
    delete_object(imagekey)
    # delete metadata row from images_metadata
    deleteImageMetadata(session['username'], imagekey)
    return redirect("/view")
