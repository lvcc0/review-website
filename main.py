from flask import Flask, render_template, redirect
import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from forms.register import RegisterForm
from forms.login import LoginForm
from forms.review import ReviewForm

from data import db_session
from data.users import User
from data.reviews import Review


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_one_is_hella_secret'
app.config['PERMAMENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init('db/db.sqlite')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html', title='Cool website :0')


@app.route('/register', methods=['GET', 'POST'])
def register():
    db_sess = db_session.create_session()
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration', form=form,
                                   message="Password don't match, try again.")

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration', form=form,
                                   message="There is already a user registered with that email.")
        
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
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        
        return render_template('login.html',  message="Incorrect mail or password", form=form)
    
    return render_template('login.html', title='Login', form=form)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@login_required
@app.route('/review', methods=['GET', 'POST'])
def review():
    form = ReviewForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        review = Review()
        review.positive = form.positive.data
        review.content = form.content.data
        review.is_private = form.is_private.data

        current_user.reviews.append(review)
        db_sess.merge(current_user)
        db_sess.commit()

        return redirect('/')
    
    return render_template('review.html', title='Reviewing a game', form=form)


def main():
    app.run()


if __name__ == '__main__':
    main()
