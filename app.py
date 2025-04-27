import flask_login
from flask import Flask, render_template, redirect, request
from data import db_session
from data.catalog import Catalog
from data.country import Country
from data.kategory import Kategory
from data.reserve import Reserve
from data.sign_up import Sign_up
from forms.LoginForm import LoginForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required
import sys

from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт
import requests
from PIL import Image
from apy.geocoder import geocode, get_coordinates, get_ll_span
from apy.show_maps import show_map

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

global db_session


def main():
    db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    catal = db_sess.query(Reserve).first()
    print(catal)



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
            return render_template('index.html', data=catal)
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
        #torbanaa22@mail.ru
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

@app.route('/logout')
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
        '''if place == '':
            toponym_to_find = 'Барнаул, ул. А. Петрова, 247А'
        else:
            toponym_to_find = place'''

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
            if tov_r is None:
                res = Reserve(id_tov=id, quantity=quant, price=num.price, kategory_id=num.kategory_id,
                              address=place, user_id = us.id, name=us.name, surname=us.surname)
                db_sess.add(res)
                db_sess.commit()
            else:
                res = db_sess.query(Reserve).filter(Reserve.id_tov == int(id)).first()
                res.quantity += int(quant)
                db_sess.commit()

    else:
        toponym_to_find = 'Барнаул, ул. А. Петрова, 247А'
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        num = db_sess.query(Catalog).get(id)

    # Пусть наше приложение предполагает запуск:
    # python search.py Москва, ул. Ак. Королева, 12
    # Тогда запрос к геокодеру формируется следующим образом:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "geocode": toponym_to_find,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        # обработка ошибочной ситуации
        pass
    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.005"
    apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "apikey": apikey,
    }
    ll = ",".join([toponym_longitude, toponym_lattitude])
    k = str(toponym_longitude)
    h = str(toponym_lattitude)

    map_api_server = "https://static-maps.yandex.ru/v1"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    im = BytesIO(response.content)
    opened_image = Image.open(im)
    maps = opened_image  # Создадим картинку и тут же ее покажем встроенным просмотрщиком операционной системы

    '''db_session.global_init("db/site.db")
    db_sess = db_session.create_session()
    num = db_sess.query(Catalog).get(id)
    tov = db_sess.query(Catalog).filter(Catalog.id == int(id)).first()
    tov.quantity -= quant
    db_sess.commit()
    tov_r = db_sess.query(Reserve).filter(Reserve.id_tov == int(id)).first()
    if tov_r == '':
        res = Reserve(id_tov=id, quantity=num.quantity, price=num.price, kategory_id=num.kategory_id, address=place)
        db_sess.add(res)
        db_sess.commit()
    else:
        res = db_sess.query(Reserve).filter(Reserve.id_tov == int(id)).first()
        res.quantity += quant
        db_sess.commit()'''



    return render_template('order.html', data=num, maps = ll, lon = k, lat = h)


@app.route('/back/<int:id>')
@login_required
def back(id):
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
            reser = db_sess.query(Reserve).all()
            return render_template('basket.html', data=reser)
        else:
            db_session.global_init("db/site.db")
            db_sess = db_session.create_session()
            reser = db_sess.query(Reserve).join(Kategory).filter(Reserve.name.like(f'%{sear}%')).all()
            return render_template('basket.html', data=reser)


    else:
        db_session.global_init("db/site.db")
        db_sess = db_session.create_session()
        us = flask_login.current_user
        reser = db_sess.query(Reserve).filter(Reserve.user_id == us.id)
        return render_template('basket.html', data=reser)




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
    main()