# Custom error handlers
# Note: for all other view functions, the default 200 status code (successfull response) is returned

from flask import render_template
from app import app, db

# Not found error template
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Internal server error template
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # reset session to a clean state to avoid failed database session to interfer with any database accesses triggered
    return render_template('500.html'), 500