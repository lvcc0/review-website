import flask
from flask import jsonify

from . import db_session
from .users import User
from .reviews import Review
from .users_to_reviews import Association


blueprint = flask.Blueprint(
    'review_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/reviews')
def get_reviews():
    db_sess = db_session.create_session()
    reviews = db_sess.query(Review).filter(Review.is_private == False).all()

    return jsonify({
        'reviews':
            [item.to_dict(only=('content', 'positive', 'created_date')) for item in reviews]
    })


@blueprint.route('/api/reviews/<int:review_id>')
def get_review(review_id):
    db_sess = db_session.create_session()
    review = db_sess.query(Review).filter(Review.id == review_id).filter(Review.is_private == False).first()

    return jsonify({
        int(review_id): review.to_dict(only=('content', 'positive', 'created_date'))
    })
