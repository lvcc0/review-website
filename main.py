from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import datetime
import requests

from forms.register import RegisterForm
from forms.login import LoginForm
from forms.review import ReviewForm
from forms.addgame import AddGameForm

from data import db_session
from data.users import User
from data.reviews import Review
from data.users_to_reviews import Association
from data.game_status import Status


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
    db_sess = db_session.create_session()
    form = LoginForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        
        return render_template('login.html',  message="Incorrect mail or password", form=form)
    
    return render_template('login.html', title='Login', form=form)


@app.route('/review', methods=['GET', 'POST'])
@login_required
def review():
    db_sess = db_session.create_session()
    form = ReviewForm()

    if form.validate_on_submit():

        review = Review()
        review.positive = form.positive.data
        review.steam_id = form.steam_id.data
        review.content = form.content.data
        review.is_private = form.is_private.data
        db_sess.add(review)
        db_sess.commit()

        association = Association()
        association.user_id = current_user.id
        association.review_id = review.id
        db_sess.add(association)
        db_sess.commit()

        return redirect('/')
    
    return render_template('review.html', title='Reviewing a game', form=form)


@app.route('/add_game/', methods=['GET', 'POST'])
@app.route('/add_game/<int:game_id>', methods=['GET', 'POST'])
@login_required
def add_game(game_id=None):
    db_sess = db_session.create_session()
    form = AddGameForm()

    if game_id != None:
        form.steam_id.data = game_id

    if form.validate_on_submit():

        status = Status()
        status.user_id = current_user.id
        status.steam_id = form.steam_id.data
        status.status = form.status.data

        db_sess.add(status)
        db_sess.commit()

        return render_template('add_game.html',
                               message=f'You added {status.steam_id} to your {AddGameForm.status_list[status.status]} list!',
                               form=form)
    
    return render_template('add_game.html', title='Adding a game', form=form)


@app.route('/user/<int:user_id>', methods=['GET'])
def user_account(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == user_id).first()
    associations = db_sess.query(Association).filter(Association.user_id == user_id).all()
    reviews = [db_sess.query(Review).filter(Review.id == ass.review_id).first() for ass in associations]

    return render_template('user_account.html', title=user.nickname, user=user, reviews=reviews)


@app.route('/user')
@login_required
def user_settings():
    db_sess = db_session.create_session()

    game_status = db_sess.query(Status).filter(Status.user_id == current_user.id).all()
    associations = db_sess.query(Association).filter(Association.user_id == current_user.id).all()
    reviews = [db_sess.query(Review).filter(Review.id == ass.review_id).first() for ass in associations]

    return render_template('user_settings.html', title=f'{current_user.nickname} settings and stuff',
                           game_status=game_status, status_list=AddGameForm.status_list,
                           reviews=reviews, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')    


@app.route('/game/<int:game_id>')
def game_page(game_id):
    data = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={game_id}&cc=EE&l=english&v=1').json()
    table_data = {
        'Developer': ', '.join(data[str(game_id)]['data']['developers']),
        'Publisher': ', '.join(data[str(game_id)]['data']['publishers']),
        'Release date': data[str(game_id)]['data']['release_date']['date']
    }

    if not data[str(game_id)]['success']:
        return redirect('/')

    return render_template('game_page.html', title=data[str(game_id)]['data']['name'],
                           data=data[str(game_id)]['data'], table_data=table_data,
                           game_id=game_id, current_user=current_user)


@app.errorhandler(401)
def invalid_auth(e):
    return redirect('/')


def main():
    app.run()


if __name__ == '__main__':
    main()


# TODO errorhandler redirect template
# TODO when writing down the steam game id, show the actual game somewhere near
# TODO add fancy review listing page to user public profile
# TODO add some tops and stuff to the front page
# TODO add search bar in navbar in base.html to search by id
