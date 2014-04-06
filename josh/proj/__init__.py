# create a Flask instance.
# name is the name of the package of this application and it is passed to an instance of Flask.
# It acts as the central registry for view functions, URL rules, template configuration, and more.
from flask import Flask

app = Flask(__name__)

# import the views module
from proj import views