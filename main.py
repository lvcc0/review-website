from flask import Flask, render_template

from data import db_session
from data.users import User


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_one_is_hella_secret'

db_session.global_init('db/db.sqlite')
db_sess = db_session.create_session()


@app.route('/')
def index():
    return render_template('index.html')


def main():
    global db_sess

    app.run()


if __name__ == '__main__':
    main()
