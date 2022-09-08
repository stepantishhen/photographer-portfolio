import os

from flask import Flask, render_template, redirect, request, flash, send_from_directory
from flask_mail import Mail, Message
from flask_ngrok import run_with_ngrok
from validate_email import validate_email
from werkzeug.utils import secure_filename

from data import db_session
from data.users import Post

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__, static_folder=os.path.abspath('static'))
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'photography_portfolio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'stepantishhen@mail.ru'  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = 'stepantishhen@mail.ru'  # и здесь
app.config['MAIL_PASSWORD'] = '3e3tp5jYmMRRkjG4FGRf'
mail = Mail(app)

try:
    os.mkdir(UPLOAD_FOLDER)
except FileExistsError:
    pass


@app.route('/', methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    return render_template('index.html', posts=posts)


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/genres', methods=['GET', 'POST'])
def genres():
    return render_template('genres.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        message = request.form.get('message')
        msg = Message(f'{fname} {lname}', sender='stepantishhen@mail.ru', recipients=['stepantishhen@mail.ru'])
        msg.body = message + email
        if validate_email(email):
            mail.send(msg)
            msg = Message('Ваше сообщение было успешно отправлено!', sender='stepantishhen@mail.ru', recipients=[email])
            msg.body = 'Ваше сообщение было успешно отправлено!' + message
            mail.send(msg)
    return render_template('contact.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post = Post(image=file.filename, heading=request.form.get('description'))
            db_sess.add(post)
            db_sess.commit()
    return render_template('add_post.html')


@app.route('/delete_post/<id>', methods=['GET', 'POST'])
def delete_post(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(id)
    db_sess.delete(post)
    db_sess.commit()
    return redirect('/admin')


@app.route('/single/<int:id>', methods=['GET', 'POST'])
def single(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(id)
    some_posts = db_sess.query(Post).all()[:3]
    return render_template('single.html', post=post, some_posts=some_posts)


@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    return render_template('admin-panel.html', posts=posts)


if __name__ == '__main__':
    db_session.global_init("db/main.sqlite")
    app.run(debug=True)
