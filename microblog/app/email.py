from flask import render_template
from flask_mail import Message
from app import app, mail
from threading import Thread

# Send emails asynchronously
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# Email sending wrapper function
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    # run the send_async_email in background thread, invoked by Thread 
    Thread(target=send_async_email, args=(app, msg)).start()

# Send password reset email function
def send_password_reset_email(user):
    token = user.get_reset_password_token()

    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body = render_template('email/reset_password.txt', user=user, token=token),
               text_html = render_template('email/reset_password.html', user=user, token=token))