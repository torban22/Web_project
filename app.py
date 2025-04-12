from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/log_in')
def log_in():
    return render_template('log_in.html')




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')