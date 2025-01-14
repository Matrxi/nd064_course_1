import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
total_db_connections = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    global total_db_connections
    total_db_connections += 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    global total_db_connections
    total_db_connections += 1
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    global total_db_connections
    total_db_connections += 1
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Non Existing article accessed - returning 404 page')
      return render_template('404.html'), 404
    else:
      message= 'Article ' + str(post['title']) + ' retrieved!'
      app.logger.info(message)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About us page retrieved!')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            global total_db_connections
            total_db_connections += 1
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            message = 'New article : ' + str(title) + ' created'
            app.logger.info(message)
            return redirect(url_for('index'))
    return render_template('create.html')


# Defining the Healthcheck endpoint
@app.route('/healthz')
def healthcheck():
   response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
   app.logger.info('Healthcheck function reached')
   return response

# Defining the metrics endpoint
@app.route('/metrics')
def metrics():
   connection = get_db_connection()
   global total_db_connections
   total_db_connections += 1
   total_posts = connection.execute('SELECT count(*) FROM posts').fetchone()
   response = app.response_class(
        response=json.dumps({"data": {"db_connection_count": total_db_connections, "post_count": total_posts[0]}}),
        status=200,
        mimetype='application/json'
    )
   connection.close()
   app.logger.info('Metrics function reached')
   return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
   app.run(host='0.0.0.0', port='3111')
