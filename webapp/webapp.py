from flask import Flask, request, render_template
app = Flask(__name__)


@app.route('/')
def home(user=None):
    user = user or 'Shalabh'
    return render_template('index.html', user=user)