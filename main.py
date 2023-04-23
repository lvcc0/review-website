from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import desc
from itertools import islice
import datetime
import requests

from forms.register import RegisterForm
from forms.login import LoginForm
from forms.review import ReviewForm
from forms.addgame import AddGameForm

from data import db_session, users_api, review_api
from data.users import User
from data.reviews import Review
from data.users_to_reviews import Association
from data.game_status import Status


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_one_is_hella_secret'
app.config['PERMAMENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

API_PATH_PREFIX = '/api/'

db_session.global_init('db/db.sqlite')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()

    top100in2weeks = dict(islice(requests.get('https://steamspy.com/api.php?request=top100in2weeks').json().items(), 10))
    datat100i2 = []

    for key in top100in2weeks.keys():
        datat100i2.append(requests.get(f'https://store.steampowered.com/api/appdetails/?appids={key}&cc=EE&l=english&v=1').json())

    reviews = db_sess.query(Review).filter(Review.is_private == False).order_by(desc(Review.created_date)).limit(10).all()
    assoctioations = [db_sess.query(Association).filter(Association.review_id == review.id).first() for review in reviews]
    users = [db_sess.query(User).filter(User.id == ass.user_id).first() for ass in assoctioations]
    data = []

    for review in reviews:
        game_id = review.steam_id
        req = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={game_id}&cc=EE&l=english&v=1').json()
        data.append(req[str(review.steam_id)])

    return render_template('index.html', title='Cool website :0', top100in2weeks=top100in2weeks,
                           datat100i2=datat100i2, reviews=reviews, data=data, users=users,
                           associations=assoctioations)


@app.route('/search')
def search_page():
    return redirect(f'/game/{request.args.get("q")}')


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

        if not requests.get(f'https://store.steampowered.com/api/appdetails/?appids={str(review.steam_id)}&cc=EE&l=english&v=1').json()[str(review.steam_id)]['success']:
            return render_template('review.html', title='Reviewing a game', form=form, message=f'There is no {review.steam_id} game.')

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

        if not requests.get(f'https://store.steampowered.com/api/appdetails/?appids={str(status.steam_id)}&cc=EE&l=english&v=1').json()[str(status.steam_id)]['success']:
            return render_template('add_game.html', title='Adding a game', form=form, message=f'There is no {status.steam_id} game.')        

        game = db_sess.query(Status).filter(Status.steam_id == status.steam_id).filter(Status.user_id == status.user_id).first()
        if game != None:
            return render_template('add_game.html', form=form, message=f'You already have that game in added.')

        db_sess.add(status)
        db_sess.commit()

        return render_template('add_game.html',
                               message=f'You added {status.steam_id} to your {AddGameForm.status_list[status.status]} list!',
                               form=form)
    
    return render_template('add_game.html', title='Adding a game', form=form)


@app.route('/delete_game/', methods=['GET', 'POST'])
@app.route('/delete_game/<int:game_id>', methods=['GET', 'POST'])
@login_required
def delete_game(game_id=None):
    db_sess = db_session.create_session()

    if game_id == None:
        return redirect('/')
    
    game = db_sess.query(Status).filter(Status.steam_id == game_id and Status.user_id == current_user.id).first()
    db_sess.delete(game)
    db_sess.commit()

    return redirect('/user')


@app.route('/edit_game/', methods=['GET', 'POST'])
@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_game(game_id=None):
    db_sess = db_session.create_session()
    form = AddGameForm()

    if game_id == None:
        return redirect('/')
    
    form.steam_id.render_kw = {'readonly': True}
    form.steam_id.data = game_id
    
    if form.validate_on_submit():
        status = Status()
        status.user_id = current_user.id
        status.steam_id = form.steam_id.data
        status.status = form.status.data

        if not requests.get(f'https://store.steampowered.com/api/appdetails/?appids={str(status.steam_id)}&cc=EE&l=english&v=1').json()[str(status.steam_id)]['success']:
            return render_template('edit_game.html', title='Editing a game', form=form, message=f'There is no {status.steam_id} game.')        

        game = db_sess.query(Status).filter(Status.steam_id == status.steam_id and Status.user_id == current_user.id).first()
        db_sess.delete(game)
        db_sess.commit()

        db_sess.add(status)
        db_sess.commit()

        return render_template('edit_game.html',
                               message=f'You added {status.steam_id} to your {AddGameForm.status_list[int(status.status)]} list!',
                               form=form)
    
    return render_template('edit_game.html', title='Editing a game', form=form)


@app.route('/user/<int:user_id>', methods=['GET'])
def user_account(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == user_id).first()
    game_status = db_sess.query(Status).filter(Status.user_id == user_id).all()
    associations = db_sess.query(Association).filter(Association.user_id == user_id).all()
    reviews = [db_sess.query(Review).filter(Review.id == ass.review_id).first() for ass in associations]
    data = []

    for review in reviews:
        game_id = review.steam_id
        req = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={game_id}&cc=EE&l=english&v=1').json()
        data.append(req[str(review.steam_id)])

    return render_template('user_account.html', title=user.nickname, user=user, reviews=reviews, data=data,
                           game_status=game_status, status_list=AddGameForm.status_list)


@app.route('/user')
@login_required
def user_settings():
    db_sess = db_session.create_session()

    game_status = db_sess.query(Status).filter(Status.user_id == current_user.id).all()
    associations = db_sess.query(Association).filter(Association.user_id == current_user.id).all()
    reviews = [db_sess.query(Review).filter(Review.id == ass.review_id).first() for ass in associations]
    data = []

    for game in game_status:
        game_id = game.steam_id
        req = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={game_id}&cc=EE&l=english&v=1').json()
        data.append(req[str(game.steam_id)])

    return render_template('user_settings.html', title=f'{current_user.nickname} settings and stuff',
                           game_status=game_status, status_list=AddGameForm.status_list,
                           reviews=reviews, user=current_user, data=data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')    


@app.route('/game/<int:game_id>')
def game_page(game_id):
    data = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={game_id}&cc=EE&l=english&v=1').json()

    if not data[str(game_id)]['success']:
        return redirect('/')

    table_data = {
        'Developer': ', '.join(data[str(game_id)]['data']['developers']),
        'Publisher': ', '.join(data[str(game_id)]['data']['publishers']),
        'Release date': data[str(game_id)]['data']['release_date']['date']
    }

    return render_template('game_page.html', title=data[str(game_id)]['data']['name'],
                           data=data[str(game_id)]['data'], table_data=table_data,
                           game_id=game_id, current_user=current_user)


@app.route('/change_private', methods=['POST', 'GET'])
@login_required
def change_private():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.stats_private = not user.stats_private
    db_sess.commit()

    return 'nothing'


@app.errorhandler(400)
def internal_server_error(e):
    if request.path.startswith(API_PATH_PREFIX):
        return make_response(jsonify({'error': str(e)}), 400)
    
    return render_template('error.html', title=e, e=e)


@app.errorhandler(401)
def invalid_auth(e):
    if request.path.startswith(API_PATH_PREFIX):
        return make_response(jsonify({'error': str(e)}), 401)
    
    return render_template('error.html', title=e, e=e)


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith(API_PATH_PREFIX):
        return make_response(jsonify({'error': str(e)}), 404)

    return render_template('error.html', title=e, e=e)


@app.errorhandler(500)
def internal_server_error(e):
    if request.path.startswith(API_PATH_PREFIX):
        return make_response(jsonify({'error': str(e)}), 500)
    
    return render_template('error.html', title=e, e=e)


def main():
    db_session.global_init('db/db.sqlite')

    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(review_api.blueprint)

    app.run()


if __name__ == '__main__':
    main()
