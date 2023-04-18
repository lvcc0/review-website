from flask import Flask, render_template, redirect

from forms.user import RegisterForm

from data import db_session
from data.users import User


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_one_is_hella_secret'

db_session.global_init('db/db.sqlite')
db_sess = db_session.create_session()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global db_sess
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration', form=form,
                                   message="Password don't match, try again.")

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration', form=form,
                                   message="There is alreay a user registered with that email.")
        
        user = User(
            nickname=form.nickname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    
    return render_template('register.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'u good'


def main():
    global db_sess

    app.run()


if __name__ == '__main__':
    main()
