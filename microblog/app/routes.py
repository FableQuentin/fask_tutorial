# Home page route
# Handles the different URLs that the application supports
# -> in Flask handlers for application routes are written as
#    Python functions called 'view functions'
# -> View functions are mapped to one (or more) URLs
# -> i.e Flask knows what to execute when the client request a given URL  

from flask import render_template
from app import app

# We use decorators to create an association between the URL given as argument and the function
# When a browser requests either of the two URL '/' or '/index', Flask is goinf to invoke this function
# and pass its value back to the browser
@app.route('/')
@app.route('/index')
def index():
	# 'mock' object: we don't have user yet
	user = {'username': 'Bob'}

	# list of posts for my blog
	posts = [
		{
			'author': {'username': 'Jackie Chan'},
			'body': 'Beautiful day in Caen!'
		},
		{
			'author': {'username': 'Bobby Brown'},
			'body': 'I like trains!'
		},		
	]

	# The operation that converts a template into a HTML page is called 'rendering'
	# It is done in Flask using the 'render_template(<filename.html>, <arg>)' function
	# render_templates invokes Jinja template engine (bundled with Flask)
	# Jinja substitutes {{ ... }} block with corresponding values provided in the <arg> of the function 
	return render_template('index.html', title='Home', user=user, posts=posts)
