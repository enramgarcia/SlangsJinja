import redis
from flask import Flask, request, render_template, redirect, flash

HOST = "localhost"
PORT = 6379

app = Flask(__name__)


def init_con():
    return redis.Redis(
        host=HOST,
        port=PORT,
        db=0,
        charset="utf-8",
        decode_responses=True)


def seed():
    words = [
        {'word': 'Xopa', 'description': 'Forma coloquial de decir Hola.'},
        {'word': 'Chantin', 'description': 'Casa'}
    ]

    redis_con = init_con()

    for definition in words:
        result_set = redis_con.get(definition['word'])
        if result_set is not None:
            continue

        redis_con.set(definition['word'], definition['description'])


@app.route('/palabras/crear', methods=['GET'])
def create():
    return render_template('create.html')


@app.route('/palabras/crear', methods=['POST'])
def add():
    word = request.form['word']
    description = request.form['description']

    if (word is None or word == '') or (description is None or description == ''):
        return redirect('/palabras/crear')

    redis_con = init_con()
    result_set = redis_con.get(word)

    if result_set is not None:
        redirect('/500')

    redis_con.set(word, description)

    return redirect('/')


@app.route('/palabras/<word>', methods=['GET'])
def get(word):
    redis_con = init_con()
    result_set = redis_con.get(word)

    if result_set is None:
        return redirect('/404')

    return render_template('get.html', slang={'word': word, 'description': result_set})


@app.route('/palabras/<word>/editar', methods=['GET'])
def edit(word):

    redis_con = init_con()
    result_set = redis_con.get(word)

    if result_set is None:
        return redirect('/404')

    return render_template('edit.html', slang={'word': word, 'description': result_set})


@app.route('/palabras/<word>/editar', methods=['POST'])
def put(word):
    description = request.form['description']

    if description is None or description == '':
        return redirect(f'/palabras/{word}/edit')

    redis_con = init_con()
    result_set = redis_con.get(word)

    if result_set is None:
        return redirect('/404')

    redis_con.set(word, description)

    return redirect('/')


@app.route('/palabras/<word>/borrar', methods=['GET'])
def delete(word):

    redis_con = init_con()
    result_set = redis_con.get(word)

    if result_set is None:
        return redirect('/404')

    redis_con.delete(word)

    return redirect('/')


@app.route('/')
def index():
    slangs = []
    redis_con = init_con()

    for r_key in redis_con.keys():
        slangs.append({'word': r_key, 'description': redis_con.get(r_key)})

    return render_template("index.html", slangs=slangs)


@app.route('/404')
def _404():
    return render_template("404.html")


@app.route('/500')
def _500():
    return render_template("500.html")


if __name__ == '__main__':
    app.run()

    seed()
