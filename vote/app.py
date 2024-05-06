from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import logging

option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
hostname = socket.gethostname()

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    # New code for collecting user information and movie selection
    user_info = {}
    movies = ["Romance", "Terror", "Comedia", "Suspenso", "Ficcion"]  # Sample list of movies
    
    if request.method == 'POST':
        # Collect user information
        user_info['name'] = request.form['name']
        user_info['age'] = request.form['age']
        user_info['gender'] = request.form['gender']

        # Collect selected movies
        selected_movies = []
        for movie in movies:
            if request.form.get(movie):
                selected_movies.append(movie)
        user_info['selected_movies'] = selected_movies

        # Store user information in Redis
        redis = get_redis()
        data = json.dumps({'voter_id': voter_id, 'user_info': user_info})
        redis.rpush('user_info', data)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
        movies=movies,  # Pass movies to the template for selection
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
