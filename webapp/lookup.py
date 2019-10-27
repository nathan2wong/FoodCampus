from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, make_response, session, jsonify, abort
from werkzeug.utils import secure_filename
import os
import datetime
import urllib
import google
#from google.cloud import firestore

ALLOWED_EXTENSIONS = set(['xlsx'])
TAX = 1.095
COMISSION = 1

app = Flask(__name__)
app.secret_key = os.urandom(2**16)

import firebase_admin
from firebase_admin import credentials, storage, auth, firestore

cred=credentials.Certificate('/Users/nathanwong/Desktop/FoodCampus-5de64d4d1920.json')
firebase_admin.initialize_app(cred, {
    'projectID': 'foodcampus',
    'storageBucket': 'foodcampus.appspot.com'
})

db = firestore.client()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if not checkLoggedIn():
        return render_template("splash.html")
    return redirect(url_for('homepage'))

@app.route('/login')
def login():
    return render_template("index.html", top_nav = top_nav, side_nav=side_nav, default_packages=default_packages)

@app.route('/user')
def homepage():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    try:
        bucket = storage.bucket()
        blob = bucket.blob('hello.txt')
        outfile='./hello.txt'
        blob.upload_from_filename(outfile)
    except:
        print("ok")
    def displayAllData():
        user_refs = db.collection("available options")
        docs = user_refs.stream()
        options = [doc.to_dict() for doc in docs]
        ret_dict = {}

        for option in options:
            product = option['item']
            price = option['cash_price']
            place = option["\ufeffname"]
            popularity = option["popularity"]
            if place in ret_dict:
                ret_dict[place].append({product: [price, popularity]})
            else:
                ret_dict[place] = [{product: [price, popularity]}]
        return ret_dict
    display_dict = displayAllData()


    return render_template("buyer.html", options=display_dict)


@app.route('/login/notes')
def session_login():
    id_token = request.headers.get("Authorization")
    expires_in = datetime.timedelta(days=5)
    try:
        # Create the session cookie. This will also verify the ID token in the process.
        # The session cookie will have the same claims as the ID token.
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
        response = jsonify({'status': 'success'})
        # Set cookie policy for session cookie.
        expires = datetime.datetime.now() + expires_in
        response.set_cookie(
            'session', session_cookie, expires=expires, secure=True)
        resp = make_response(render_template("analysis.html"))
        resp.set_cookie('session', session_cookie)
        return resp
    except:
        return abort(401, 'Failed to create a session cookie')

def checkLoggedIn():
    session_cookie = request.cookies.get('session')
    if not session_cookie:
        # Session cookie is unavailable. Force user to login.
        return False

    # Verify the session cookie. In this case an additional check is added to detect
    # if the user's Firebase session was revoked, user deleted/disabled, etc.
    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        return True
    except:
        # Session cookie is invalid, expired or revoked. Force user to login.
        return False
#For testing
@app.route("/<path:path>")
def images(path):
    resp = make_response(open(path).read())
    resp.content_type = "image/png"
    return resp

@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        user_refs = db.collection("available options")
        docs = user_refs.stream()
        options = [doc.to_dict() for doc in docs]
        ret_dict = {}

        for option in options:
            product = option['item']
            price = option['cash_price']
            place = option["\ufeffname"]
            popularity = option["popularity"]
            if place in ret_dict:
                ret_dict[product].append([place, price, popularity]) #NEED TO FIX THIS LOL
            else:
                ret_dict[product] = [place, price, popularity]

        raw_cost = 0.0
        reqs = []
        item_dict = {}
        for item in request.form:
            if len(request.form[item]) > 0 and item != "example_length":
                reqs += [item] * int(request.form[item])
        for item in reqs:
            if item in ret_dict:
                raw_cost += float(ret_dict[item][1])
                if item not in item_dict:
                    item_dict[item] = 1
                else:
                    item_dict[item] += 1
        post_tax = raw_cost * TAX
        with_commission = max(post_tax + 1, post_tax + 0.08 *raw_cost)
        raw, actual = round(post_tax, 2), round(with_commission, 2)
        comission = round(actual-raw, 2)
        return render_template('buyer.html', raw=raw, comission=comission, actual=actual, item_dict=item_dict)

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/deliver")
def deliver():
    return render_template("deliver.html")
@app.route("/mapbox")
def mapbox():
    return render_template("mapbox.html")

top_nav = '''<nav class="navbar navbar-expand navbar-dark bg-dark static-top">

  <a class="navbar-brand mr-1" href="/">Data Visualize</a>

  <button class="btn btn-link btn-sm text-white order-1 order-sm-0" id="sidebarToggle" href="#">
    <i class="fas fa-bars"></i>
  </button>


</nav>'''

side_nav = '''<ul class="sidebar navbar-nav">
    <li class="nav-item active">
      <a class="nav-link" href="/">
        <i class="fas fa-fw fa-tachometer-alt"></i>
        <span>Home</span>
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="/user">
        <i class="fas fa-fw fa-chart-area"></i>
        <span>User Application</span></a>
    </li>
  </ul>'''

default_packages = ''' <!-- Custom fonts for this template-->
  <link href="{{ url_for('static',filename='vendor/fontawesome-free/css/all.min.css') }}" rel="stylesheet" type="text/css">
  <!-- Custom styles for this template-->
  <script src="https://www.gstatic.com/firebasejs/7.2.2/firebase-app.js"></script>

  <!-- TODO: Add SDKs for Firebase products that you want to use
       https://firebase.google.com/docs/web/setup#available-libraries -->
  <script src="https://www.gstatic.com/firebasejs/7.2.2/firebase-analytics.js"></script>
  <script src="https://www.gstatic.com/firebasejs/7.2.2/firebase.js"></script>

  <link href="{{ url_for('static',filename='css/sb-admin.css') }}" rel="stylesheet">
  <script src="https://cdn.firebase.com/libs/firebaseui/3.5.2/firebaseui.js"></script>
  <link type="text/css" rel="stylesheet" href="https://cdn.firebase.com/libs/firebaseui/3.5.2/firebaseui.css" />
  <script src="{{ url_for('static',filename='vendor/jquery/jquery.min.js') }}"></script>
  <script src="{{ url_for('static',filename='vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>

  <!-- Custom scripts for all pages-->
  <script src="{{ url_for('static',filename='js/sb-admin.min.js') }}"></script>
  <!-- The core Firebase JS SDK is always required and must be listed first -->

  <script src="{{ url_for('static', filename='js/firebase_js.js') }}"></script>'''
