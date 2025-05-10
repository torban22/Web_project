import os
import flask_login
from flask import Flask, render_template, redirect, request, flash
from werkzeug.utils import secure_filename
from data import db_session
from data.catalog import Catalog
from data.country import Country
from data.kategory import Kategory
from data.reserve import Reserve
from data.sign_up import Sign_up
from forms.AdminLogForm import AdminLogForm
from forms.LoginForm import LoginForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required
from io import BytesIO
import requests
from PIL import Image


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

global db_session

@app.route('/', methods=['POST', 'GET'])
@app.route('/index/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        sear = request.form.get('search')
        if sear == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            catal = db_sess.query(Catalog).all()
            return render_template('index.html', data=catal)
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            catal = db_sess.query(Catalog).join(Kategory).filter(Catalog.name.like(f'%{sear}%')).all()
            return render_template('index.html', data=catal)
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        catal = db_sess.query(Catalog).all()
        return render_template('index.html', data = catal)

@app.route('/index/<string:num>/', methods=['POST', 'GET'])
def index_sort(num):
    if request.method == 'POST':
        sear = request.form.get('search')
        if sear == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            nm = db_sess.query(Catalog).join(Kategory).filter(Kategory.kategor == num).all()
            return render_template('index_sort.html', data=nm)
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            catal = db_sess.query(Catalog).join(Kategory).filter(Catalog.name.like(f'%{sear}%'), Kategory.kategor == num).all()
            return render_template('index_sort.html', data=catal)
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        nm = db_sess.query(Catalog).join(Kategory).filter(Kategory.kategor == num).all()
        return render_template('index_sort.html', data=nm)

@app.route('/index/<int:id>')
def index_detail(id):
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    num = db_sess.query(Catalog).get(id)
    return render_template('index_detail.html', data = num)

@app.route('/basket/<int:id>')
def basket_detail(id):
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    num = db_sess.query(Catalog).get(id)
    return render_template('index_detail.html', data = num)

@app.route('/register/', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Sign_up).filter(Sign_up.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = Sign_up(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=form.password.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Sign_up).get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Sign_up).filter(Sign_up.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
def order(id):
    if request.method == 'POST':
        place = request.form.get('place')
        quant = request.form.get('quantity')
        if quant == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            num = db_sess.query(Catalog).get(id)
            return render_template('order.html', data=num, message='Не задано количество')
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            num = db_sess.query(Catalog).get(id)
            if place == '':
                return render_template('order.html', data=num, message = 'Не задан адрес')
            else:
                toponym_to_find = place
            tov = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
            tov.quantity -= int(quant)
            db_sess.commit()
            us = flask_login.current_user
            tov_r = db_sess.query(Reserve).filter(Reserve.id_tov == int(id), Reserve.user_id == int(us.id)).first()

            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
            geocoder_params = {
                "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
                "geocode": toponym_to_find,
                "format": "json"}
            response = requests.get(geocoder_api_server, params=geocoder_params)
            if not response:
                pass
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            k = str(toponym_longitude)
            h = str(toponym_lattitude)
            if tov_r is None:
                res = Reserve(id_tov=id, quantity=quant, price=num.price, kategory_id=num.kategory_id,
                              lon=k, lat=h, user_id = us.id, name=us.name, surname=us.surname)
                db_sess.add(res)
                db_sess.commit()
            else:
                res = db_sess.query(Reserve).filter(Reserve.id_tov == int(id)).first()
                res.quantity += int(quant)
                db_sess.commit()
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        num = db_sess.query(Catalog).get(id)
        k = str(83.776856)
        h = str(53.346785)
    return render_template('order.html', data=num, lon = k, lat = h)

@app.route('/back/<int:id>', methods=['GET', 'POST'])
@login_required
def back(id):
    print(id)
    us = flask_login.current_user
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    res = db_sess.query(Reserve).filter(Reserve.id_tov == int(id), Reserve.user_id == int(us.id)).first()
    tov = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
    tov.quantity += int(res.quantity)
    db_sess.delete(res)
    db_sess.commit()
    return redirect("/basket")

@app.route('/basket', methods=['POST', 'GET'])
def basket():
    if request.method == 'POST':
        sear = request.form.get('search')
        if sear == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            us = flask_login.current_user
            reser = db_sess.query(Reserve).filter(Reserve.user_id == us.id)
            return render_template('basket.html', data=reser)
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            us = flask_login.current_user
            reser = db_sess.query(Reserve).join(Catalog).filter(Catalog.name.like(f'%{sear}%'), Reserve.user_id == us.id).all()
            return render_template('basket.html', data=reser)
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        us = flask_login.current_user
        reser = db_sess.query(Reserve).filter(Reserve.user_id == us.id)
        return render_template('basket.html', data=reser)

@app.route('/basket/<string:num>/')
def basket_sort(num):
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    us = flask_login.current_user
    nm = db_sess.query(Reserve).join(Kategory).filter(Kategory.kategor == num, Reserve.user_id == us.id).all()
    return render_template('basket_sort.html', data=nm)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLogForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Sign_up).filter(Sign_up.email == form.email.data, Sign_up.name == 'Admin').first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/admin_index/")
        return render_template('admin_login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('admin_login.html', title='Авторизация', form=form)

@app.route('/admin_index/', methods=['POST', 'GET'])
def admin_index():
    if request.method == 'POST':
        sear = request.form.get('search')
        if sear == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            catal = db_sess.query(Catalog).all()
            return render_template('admin_index.html', data=catal)
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            catal = db_sess.query(Catalog).join(Kategory).filter(Catalog.name.like(f'%{sear}%')).all()
            return render_template('admin_index.html', data=catal)
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        catal = db_sess.query(Catalog).all()
        return render_template('admin_index.html', data = catal)

@app.route('/admin_index/<int:id>')
def admin_detail(id):
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    num = db_sess.query(Catalog).get(id)
    return render_template('admin_detail.html', data = num)

@app.route('/admin_index/<string:num>/', methods=['POST', 'GET'])
def admin_sort(num):
    if request.method == 'POST':
        sear = request.form.get('search')
        if sear == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            nm = db_sess.query(Catalog).join(Kategory).filter(Kategory.kategor == num).all()
            return render_template('admin_sort.html', data=nm)
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            catal = db_sess.query(Catalog).join(Kategory).filter(Catalog.name.like(f'%{sear}%'), Kategory.kategor == num).all()
            return render_template('admin_sort.html', data=catal)
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        nm = db_sess.query(Catalog).join(Kategory).filter(Kategory.kategor == num).all()
        return render_template('admin_sort.html', data=nm)

@app.route('/admin_back/<int:id>', methods=['GET', 'POST'])
def admin_back(id):
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    res = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
    im = res.image
    relative_path = f"static/{im}"
    absolute_path = os.path.abspath(relative_path)
    os.remove(absolute_path)
    db_sess.delete(res)
    db_sess.commit()
    return redirect("/admin_index")

UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin_add/', methods=['GET', 'POST'])
def admin_add():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('admin_add.html', message='Не могу прочитать файл')
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            name = request.form.get('name')
            kategory = request.form.get('kategory')
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            country = request.form.get('country')
            haracteristic = request.form.get('haracteristic')
            image = filename
            count_id = db_sess.query(Country).filter(Country.title == country).first()
            kat_id = db_sess.query(Kategory).filter(Kategory.kategor == kategory).first()
            cat = Catalog(name=name, kategory_id=str(kat_id), quantity=quantity, price=price, country_id=str(count_id), haracteristic=haracteristic, image=image)
            db_sess.add(cat)
            db_sess.commit()
            return render_template('admin_add.html', message='Успешно')
    else:
        return render_template('admin_add.html')

@app.route('/admin_change/<int:id>', methods=['GET', 'POST'])
def admin_change(id):
    if request.method == 'POST':
        file = request.files['file']
        if 'file' not in request.files:
            return render_template('admin_change.html', message='Не могу прочитать файл')
        elif file.filename == '':
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            name = request.form.get('name')
            kategory = request.form.get('kategory')
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            country = request.form.get('country')
            haracteristic = request.form.get('haracteristic')
            count_id = db_sess.query(Country).filter(Country.title == country).first()
            kat_id = db_sess.query(Kategory).filter(Kategory.kategor == kategory).first()
            cat = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
            cat.name = name
            cat.kategory_id = str(kat_id)
            cat.quantity = quantity
            cat.price = price
            cat.country_id = str(count_id)
            cat.haracteristic = haracteristic
            db_sess.commit()
            num = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
            return render_template('admin_change.html', data=num, message='Успешно')
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            name = request.form.get('name')
            kategory = request.form.get('kategory')
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            country = request.form.get('country')
            haracteristic = request.form.get('haracteristic')
            image = filename
            count_id = db_sess.query(Country).filter(Country.title == country).first()
            kat_id = db_sess.query(Kategory).filter(Kategory.kategor == kategory).first()
            cat = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
            im = cat.image
            relative_path = f"static/{im}"
            absolute_path = os.path.abspath(relative_path)
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), im)
            os.remove(absolute_path)
            cat.name = name
            cat.kategory_id = str(kat_id)
            cat.quantity = quantity
            cat.price = price
            cat.country_id = str(count_id)
            cat.haracteristic = haracteristic
            cat.image = image
            db_sess.commit()
            num = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
            return render_template('admin_change.html', data=num, message='Успешно (изображение загружено)')
    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        num = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
        return render_template('admin_change.html', data=num, message='')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
