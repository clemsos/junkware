from gevent import monkey
monkey.patch_all()

import os, time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit
import jinja2
import ast, json
from lib.queue import RedisQueue


# server 
# from http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
app = Flask(__name__, static_folder='ui')
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None

# custom UI location
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('ui'),
])
app.jinja_loader = my_loader


# data queue
q = RedisQueue('mindwave')

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(1)
        count += 1
        point = q.get()
        point = ast.literal_eval(point)
        
        socketio.emit('point',
                      {'data': point, 'count': count},
                      namespace='')


@app.route('/')
def index():
    global thread
    if thread is None:
        print 'start thread'
        thread = Thread(target=background_thread)
        thread.start()
    return render_template('index.html')


@socketio.on('my event', namespace='')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('connect', namespace='')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='')
def test_disconnect():
    print('Client disconnected')

# STATIC
@app.route('/js/<path:path>')
def js_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))

@app.route('/css/<path:path>')
def css_static_proxy(path):
    print path
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))

@app.route('/lib/<path:path>')
def lib_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('lib', path))

if __name__ == '__main__':
    socketio.run(app)
