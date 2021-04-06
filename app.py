from flask import Flask, flash, url_for, render_template, request
from flask_login import LoginManager, login_required, login_user, current_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import os
from pathlib import Path
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import redirect, secure_filename
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


# Constants
UPLOAD_PATH = Path(__file__).parent.absolute().joinpath('file_uploads')
UPLOAD_FOLDER = str(UPLOAD_PATH)

# Create directory, if it does not exist
os.makedirs(UPLOAD_PATH, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///docs.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '(id: {}, user: {})'.format(self.id, self.username)


class Attribute(db.Model):
    __tablename__ = 'attribute'
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    attribute_key = db.Column(db.String(250), unique=True, nullable=False)
    attribute_value = db.Column(db.String(250), nullable=False)

    # Possible alternative
    # doc_id = db.Column(db.Integer, db.ForeignKey('document.id'), primary_key=True)
    # attribute_key = db.Column(db.String(250), primary_key=True)
    # attribute_value = db.Column(db.String(250), nullable=False)

    def __init__(self, doc_id, key, value):
        self.doc_id = doc_id
        self.attribute_key = key
        self.attribute_value = value

    def __repr__(self):
        return '(doc_id {}: {}:{})'.format(self.doc_id, self.attribute_key, self.attribute_value)


class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    doc = db.Column(db.String, nullable=False)
    ocr = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a relationship using a dictionary collection
    # https://docs.sqlalchemy.org/en/13/orm/collections.html#dictionary-collections
    doc_attributes = db.relationship('Attribute', collection_class=attribute_mapped_collection('attribute_key'))

    # Proxy the attributes relationship to produce a view
    # https://docs.sqlalchemy.org/en/14/orm/extensions/associationproxy.html#proxying-to-dictionary-based-collections
    association_proxy('doc_attributes', 'value', creator=lambda k, v: Attribute(attribute_key=k, attribute_value=v))

    def __init__(self, document, user_id):
        self.doc = document
        self.user_id = user_id

    def __repr__(self):
        return '(id: {}, doc: {})'.format(self.id, self.doc)

    @classmethod
    def with_attributes(cls, key, value):
        return cls.attributes.any(key=key, value=value)


# Initialize database
db.create_all()

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    Returns the User object, if it exists in database. Else None is returned.
    """
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    """
    Form for login html
    """
    username = StringField('username', [DataRequired()])
    password = PasswordField('password', [DataRequired()])
    submit = SubmitField('Submit')


@app.route(rule='/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Login failed. User or password invalid')
            return redirect(url_for('login'))
        flash('Login successful')
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route(rule='/', methods=['GET'])
@app.route(rule='/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@app.route(rule='/add_doc', methods=['GET', 'POST'])
@login_required
def add_doc():
    """
    Store document in filesystem on server and the file name in database

    :return:
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file request')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and file.filename.lower().endswith('pdf'):
            filename = secure_filename(file.filename)
            # Upload file to upload_folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Store file path in database
            doc = Document(file.filename, current_user.id)
            db.session.add(doc)
            db.session.commit()

            flash('File successfully uploaded: {}'.format(file.filename))
            return redirect(url_for('index'))
        else:
            flash('File must be a pdf')
            return redirect(request.url)
    return render_template('add_doc.html')


def get_dummy_ocr_results():
    return {
        "extracted_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    }


@app.route(rule='/run_ocr', methods=['GET', 'POST'])
@login_required
def run_ocr():
    if request.method == 'POST':
        ocr_result = get_dummy_ocr_results()
        try:
            doc_id = int(request.form.get('doc_id', 0))
            if doc_id == 0:
                flash('Document id does not exist')

        except Exception:
            flash('Please enter a valid document id')
            return redirect(request.url)

        db.session.execute("UPDATE document SET ocr = '{}' WHERE id = {} AND user_id = {}".format(
                ocr_result.get('extracted_text', ''), doc_id, current_user.id))

        db.session.commit()

        flash('OCR analysis successful, results:\n{}'.format(ocr_result.get('extracted_text', '')))

    return render_template('run_ocr.html')


@app.route(rule='/list_docs', methods=['GET'])
@login_required
def list_docs():
    """
    Get all documents from database of currently logged-in user

    :return:
    """
    rows = db.session.execute("SELECT id, doc, ocr FROM document WHERE user_id = {}".format(current_user.id))
    return render_template('list_docs.html', rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
