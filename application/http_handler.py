import flask
import application.gcp_handler as gcp
from flask_session import Session
from secrets import token_urlsafe

# Main Application
app = flask.Flask(__name__)

# Configurations
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True

# Flask-Session stuff
app.config.from_object(__name__)
Session(app)
flask.Flask.secret_key = token_urlsafe(16)

REQUEST_TEMPLATE = 'request.html.jinja'


@app.route('/')
def index():
    return flask.redirect(flask.url_for('.request'))


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    print("Session ID => ", id(flask.session))
    key_contents = flask.session.get('key_contents')
    is_cred_valid, message = gcp.check_valid_creds(key_contents)
    if flask.request.method == 'GET':
        return flask.render_template(
            'auth.html.jinja',
            is_cred_valid=is_cred_valid,
            message=message
        )
    service_account_cred_file = flask.request.files.get('cred_file')
    if not service_account_cred_file:
        raise Exception('File not found !')
    key_contents = service_account_cred_file.read()
    is_cred_valid, message = gcp.check_valid_creds(key_contents)

    if is_cred_valid:
        flask.session['key_contents'] = key_contents
    return flask.render_template(
        'auth.html.jinja',
        is_cred_valid=is_cred_valid,
        message=message
    )


@app.route('/request', methods=['GET', 'POST'])
def request():
    key_contents = flask.session.get('key_contents')
    if not key_contents:
        return flask.redirect(flask.url_for('.auth'))

    if flask.request.method == 'GET':
        return flask.render_template(REQUEST_TEMPLATE)

    auth_session = gcp.get_authorised_session(
        authorisation_type=gcp.AuthorisationType.SERVICE_ACCOUNT,
        key_contents=key_contents
    )

    request_url: str = flask.request.form['request_url']
    request_type: str = flask.request.form['request_type'].upper()

    request_body: str = flask.request.form['request_body'].strip()

    res_code, res_text = gcp.make_request(
        request_type=request_type, auth_session=auth_session, request_url=request_url, data=request_body)

    return flask.render_template(
        REQUEST_TEMPLATE,
        res_code=res_code,
        res_text=res_text,
        request_url=request_url,
        request_type=request_type,
        request_body=request_body
    )
