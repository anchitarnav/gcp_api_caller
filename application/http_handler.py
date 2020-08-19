import flask
import application.gcp_handler as gcp
from flask_session import Session

app = flask.Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)


@app.route('/')
def index():
    return flask.redirect(flask.url_for('.request'))


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    #temp code. Get this from HTML form
    service_account_cred_file = '/Users/aarnav/Downloads/Cloud-Accounts/file_name.json'
    with open(service_account_cred_file) as fp:
        key_contents = fp.read()

    flask.session['key_contents'] = key_contents
    return "Auth Set successfully !!"


@app.route('/request', methods=['GET', 'POST'])
def request():
    key_contents = flask.session.get('key_contents')
    if not key_contents:
        return flask.redirect(flask.url_for('.auth'))

    if flask.request.method == 'GET':
        return flask.render_template(
            'request.html.jinja'
        )

    auth_session = gcp.get_authorised_session(
        authorisation_type=gcp.AuthorisationType.SERVICE_ACCOUNT,
        key_contents=key_contents
    )

    request_url = flask.request.form.get('request_url')
    request_type = getattr(gcp.GoogleRequests, flask.request.form.get('request_type', 'UNKNOWN_REQUEST'), None)
    if not request_type:
        raise Exception('Illegal Request type')
    res_code, res_text = gcp.make_request(request_type=gcp.GoogleRequests.GET, auth_session=auth_session, request_url=request_url)
    return flask.render_template(
        'request.html.jinja',
        res_code=res_code,
        res_text=res_text
    )
