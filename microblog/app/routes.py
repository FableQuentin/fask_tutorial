# Home page route
# Handles the different URLs that the application supports
# -> in Flask handlers for application routes are written as
#    Python functions called 'view functions'
# -> View functions are mapped to one (or more) URLs
# -> i.e Flask knows what to execute when the client request a given URL  

from app import app

# We use decorators to create an association between the URL given as argument and the function
# When a browser requests either of the two URL '/' or '/index', Flask is goinf to invoke this function
# and pass its value back to the browser
@app.route('/')
@app.route('/index')
def index():
	return "Hello, World!"
