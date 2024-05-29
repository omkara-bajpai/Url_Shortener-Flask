import random
import string
from flask import Flask, render_template, request, redirect, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode   
from datetime import timedelta
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.secret_key = 'Super secret key'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)


class Urls(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    by = db.Column(db.String(200), unique=False, nullable=False)
    long_url = db.Column(db.String, nullable=False)
    short = db.Column(db.String(200), unique=True, nullable=True)
    click = db.Column(db.Integer, nullable=False)
    qr = db.Column(db.String(200), nullable=True)
    qr_image = db.Column(db.String(2000), nullable=True)
    qr_id = db.Column(db.String(2000), nullable=True)


def generate(length):
    chars = string.ascii_letters + string.digits
    shortened_url = ''.join(random.choice(chars) for i in range(length))
    return shortened_url


@app.route('/home', methods=['POST', 'GET'])
def index():

    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            long_urls = []
            short_urls = []
            clicks = []
            data = Urls.query.filter_by().all()
            for query in data:
                long_urls.append(query.long_url)
                short_urls.append(query.short)
                clicks.append(query.click)
            data = Urls.query.filter_by(by=session['user']).all()
            return render_template('dashboard.html', urls=data)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/links/<link>')
def redirect_to_link(link):
    long_urls = []
    short_urls = []
    clicks = []
    data = Urls.query.filter_by().all()
    for query in data:
        long_urls.append(query.long_url)
        short_urls.append(query.short)
        clicks.append(query.click)

    if link in short_urls:
        query = Urls.query.filter_by(short=link).first()
        query.click = query.click + 1
        db.session.add(query)
        db.session.commit()
        long_url = long_urls[short_urls.index(link)]
        clicks[short_urls.index(link)] += 1

        if long_url[0:4] == 'http':
            return redirect(long_url)
        else:
            return redirect("https://"+long_url)
    else:
        return render_template('text_show.html', text="Wrong link 404")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect('/home')
    else:

        if request.method == 'POST':
            data = User.query.filter_by().all()
            emails = []
            passs = []
            for query in data:
                emails.append(query.email)
                passs.append(query.password)
            email = request.form.get('email')
            passw = request.form.get('pass')
            if email == "" or passw == "":
                flash("Email or Password is blank")
            else:
                if email in emails:
                    if passs[emails.index(email)] == passw:
                        session['user'] = email
                        return redirect('/home')
                    else:
                        flash("Wrong email or password")
                else:
                    flash("Wrong email or password")
        return render_template('login.html')


@app.route('/')
def blank():
    if 'user' in session:
        return redirect('/home')
    else:
        return redirect('/login')


@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if 'user' in session:
        return redirect('/home')
    else:
        if request.method == 'POST':

            email = request.form.get('email')
            passw = request.form.get('pass')
            con_pass = request.form.get('con_pass')
            if email == "" or passw == "":
                flash("Email or Password is blank")
            else:
                if passw == con_pass:
                    try:
                        if len(email) < 2000 and len(passw) < 2000:
                            data = User(email=email, password=passw)
                            db.session.add(data)
                            db.session.commit()
                            session['user'] = email
                            return redirect('/home')
                        else:
                            flash('The email or password is too big')
                    except:
                        flash("Email already exists Please pick another")
                else:
                    flash("The Password is not matching the Confirm Password")

        return render_template('sign.html')


@app.route('/show/<url>')
def show(url):
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            return render_template('url_generated.html', url=url)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    if 'user' in session:
        del session['user']
        return redirect('/login')
    else:
        return redirect('/login')


@app.route('/view/<url>')
def view(url):
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            data = Urls.query.filter_by(short=url).first()
            return render_template('view.html', query=data)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/qr_show/<qr_id>')
def qr_code(qr_id):
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            query = Urls.query.filter_by(qr_id=qr_id).first()
            fname = query.qr_image
            print(fname)
            return render_template('qrcode_generated.html', fname=fname)

        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            long_urls = []
            short_urls = []
            clicks = []
            data = Urls.query.filter_by().all()
            for query in data:
                long_urls.append(query.long_url)
                short_urls.append(query.short)
            if request.method == 'POST':

                long_url = request.form.get('long_url')
                operation = request.form.get('operation')
                if long_url == "":
                    flash("The Url cant be blank")
                else:
                    if operation == 'default':
                        shortened_url = generate(6)
                        while shortened_url in short_urls:
                            shortened_url = generate(6)
                        long_urls.append(long_url)
                        short_urls.append(shortened_url)
                        clicks.append(0)
                        data = Urls(by=session['user'],
                                    long_url=long_url, short=shortened_url, click=0)
                        db.session.add(data)
                        db.session.commit()
                        # return render_template('url_generated.html', url=shortened_url)
                        return redirect(f'/show/{shortened_url}')
                    else:
                        shortened_url = generate(6)
                        while shortened_url in short_urls:
                            shortened_url = generate(6)
                        image_name = generate(6)
                        while image_name in image_names:
                            image_name = generate(6)
                        without_static = image_name + ".png"
                        short_urls.append(shortened_url)
                        image = qrcode.make(long_url)
                        image.save(f'static/qrcodes/{image_name}.png')
                        image_name = image_name + '.png'
                        image_names.append(image_name)
                        qr_id = generate(6)
                        while qr_id in qr_ids:
                            qr_id = generate(6)
                        qr_ids.append(qr_id)
                        data = Urls(
                            by=session['user'], long_url=long_url, click=0, qr='yes', qr_image=without_static, qr_id=qr_id)
                        db.session.add(data)
                        db.session.commit()
                        return redirect(f'/qr_show/{qr_id}')
                clicks.append(query.click)
            return render_template('index.html')
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/download/<fname>')
def download(fname):
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            new_name = 'static/qrcodes/'+fname
            return send_file(new_name, as_attachment=True)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/view_qr/<qr_id>')
def view_qr(qr_id):
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            query = Urls.query.filter_by(qr_id=qr_id).first()
            return render_template('view_qr.html', query=query)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/account')
def account():
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            query = User.query.filter_by(email=session['user']).first()
            return render_template('account.html', query=query)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')
        


@app.route('/account/edit', methods=['GET', 'POST'])
def account_edit():
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            if request.method == 'POST':
                new = request.form.get('email')
                query = User.query.filter_by(email=session['user']).first()
                if new != '':
                    if len(new) < 200:
                        if new != session['user']:
                            data = User.query.filter_by().all()
                            data_email = []
                            for email in data:
                                data_email.append(email.email)
                            if new not in data_email:
                                query = User.query.filter_by(
                                    email=session['user']).first()
                                query.email = new
                                db.session.add(query)
                                db.session.commit()
                                if Urls.query.filter_by(by=session['user']).first():
                                    for query in Urls.query.filter_by(by=session['user']).all():
                                        query.by = new
                                        db.session.add(query)
                                        db.session.commit()
                                session['user'] = new
                                return redirect('/account')
                            else:
                                flash('This email is already taken')
                        else:
                            return redirect('/account')
                    else:
                        flash('The email is very big')
                else:
                    flash('The email cant be blank')
            query = User.query.filter_by(email=session['user']).first()
            return render_template('account_edit.html', query=query)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/account/edit/pass', methods=['GET', 'POST'])
def account_edit_pass():
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            if request.method == 'POST':
                query = User.query.filter_by(email=session['user']).first()
                old = request.form.get('old')
                new = request.form.get('new')
                confirm = request.form.get('confirm')

                if (new != "") and (old != "") and (confirm != ''):
                    if (len(new) < 2000) and (len(confirm) < 2000):
                        if new == confirm:
                            if old == query.password:
                                query.password = new
                                db.session.add(query)
                                db.session.commit()
                                return redirect('/account')
                            else:
                                flash('The old password is wrong')
                        else:
                            flash(
                                'The new password isnt matching the new confirm password')
                    else:
                        flash('The new password cant be very big')
                else:
                    flash('Please fill every fields')

            query = User.query.filter_by(email=session['user']).first()
            return render_template('account_edit_password.html', query=query)
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/account/delete', methods=['GET', 'POST'])
def delete():
    if 'user' in session:
        data = User.query.filter_by().all()
        data_email = []
        for email in data:
            data_email.append(email.email)
        if session['user'] in data_email:
            if request.method == 'POST':
                email = request.form.get('email')
                password = request.form.get('pass')
                query = User.query.filter_by(email=session['user']).first()
                if email != "" and password != '':
                    if email == session['user'] and password == query.password:
                        db.session.delete(query)
                        db.session.commit()
                        urls_list = Urls.query.filter_by(
                            by=session['user']).all()
                        for query in urls_list:
                            db.session.delete(query)
                            db.session.commit()
                        return redirect('/login')
                    else:
                        flash('The email or password is not correct')
                else:
                    flash('The email or password cant be blank')

            return render_template('delete.html')
        else:
            del session['user']
            return redirect('/login')
    else:
        return redirect('/login')


@app.before_request
def make_session_permanent():
    session.permanent = True


with app.app_context():
    db.create_all()
long_urls = []
short_urls = []
clicks = []
image_names = []
qr_ids = []
app.run(debug=True, host='0.0.0.0',port=3000)
