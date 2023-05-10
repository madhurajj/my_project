import os
from xml.dom.minidom import Document
from flask.globals import request
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User , open_database , Document
from utils import validate_email
from werkzeug.utils import secure_filename
from predictor import *
from tensorflow.keras.models import load_model

from flask import Flask,session,flash,redirect,render_template,url_for

app = Flask(__name__)
app.secret_key = "secret"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
def session_add(key, value):
    session[key] = value


def load_tf_model(path="model_casia_run1.h5"):
    return load_model(path)

def save_file(file):
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return path

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg','tiff']


def get_db():
    engine = create_engine('sqlite:///database.sqlite')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

@app.route('/')
def index():
    return render_template('index.html',title='Home')

@app.route('/upload/document/image', methods=['GET','POST'])
def upload_document_image():
    if 'isauth' not in session:
        flash('You need to login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
         file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('dashboard'))
    if file and allowed_file(file.filename):
        path = save_file(file)
        session_add('last_document_image_path', path)
        flash('File uploaded successfully', 'success')
        db = open_database()
        user_id = session['id']
        document_image = Document(path=path, added_by=user_id)
        db.add(document_image)
        db.commit()
        return redirect(url_for('home'))
    

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and (email):
            if password and len(password)>=6:
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email,password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.name
                        del sess
                        flash('login successfull','success')
                        return redirect('/home')
                    else:
                        flash('email or password is wrong','danger')
                except Exception as e:
                    flash(e,'danger')
    return render_template('login.html',title='login')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password)>=6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(name=name,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            del sess
                            flash('registration successful','success')
                            return redirect('/')
                        except:
                            flash('email account already exists','danger')
                    else:
                        flash('confirm password does not match','danger')
                else:
                    flash('password must be of 6 or more characters','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('invalid name, must be 3 or more characters','danger')
    return render_template('signup.html',title='register')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    return render_template('forgot.html',title='forgot password')

@app.route('/home',methods=['GET','POST'])
def home():
    if session.get('isauth'):
        username = session.get('name')
        docs = get_db().query(Document).all()
        return render_template('home.html',docs=docs,title=f'Home|{username}')
    flash('please login to continue','warning')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/ReadMore')
def ReadMore():
    return render_template('ReadMore.html',title='Read More')

@app.route('/predict/<int:doc_id>/doc')
def predict(doc_id):
    doc = get_db().query(Document).filter_by(id=doc_id).first()
    model = load_tf_model()
    prediction,confidence = make_prediction(model, doc.path)
    session_add('last_prediction', prediction)
    return render_template('predict.html',prediction=prediction,title='Prediction', confidence=confidence, doc=doc)


@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True,threaded=True)
