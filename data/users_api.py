import flask
from flask import jsonify

from . import db_session
from .users import User
from .reviews import Review
from .users_to_reviews import Association
from .game_status import Status


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    
    res = []

    for user in users:
        if user.stats_private:
            res.append({
                user.id: {
                    'nickname': user.nickname,
                    'private': user.stats_private
                },
            })
        else:
            associations = db_sess.query(Association).filter(Association.user_id == user.id).all()
            reviews = [db_sess.query(Review).filter(Review.id == ass.review_id).first() for ass in associations]
            games = db_sess.query(Status).filter(Status.user_id == user.id).all()
            res.append({
                int(user.id): {
                    'nickname': user.nickname,
                    'private': user.stats_private,
                    'reviews': [item.to_dict(only=('content', 'positive', 'created_date')) for item in reviews if item.is_private == False],
                    'games': [item.to_dict(only=('steam_id', 'status')) for item in games]
                },
            })

    return jsonify(res)


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()

    if user.stats_private:
        return jsonify({
            user.id: {
                'nickname': user.nickname,
                'private': user.stats_private
            },
        })
    else:
        associations = db_sess.query(Association).filter(Association.user_id == user.id).all()
        reviews = [db_sess.query(Review).filter(Review.id == ass.review_id).first() for ass in associations]
        games = db_sess.query(Status).filter(Status.user_id == user.id).all()
        return ({
            int(user.id): {
                'nickname': user.nickname,
                'private': user.stats_private,
                'reviews': [item.to_dict(only=('content', 'positive', 'created_date')) for item in reviews],
                'games': [item.to_dict(only=('steam_id', 'status')) for item in games]
            },
        })
