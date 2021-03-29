from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from functools import wraps
from passlib.hash import sha256_crypt
from webforms import *
from lib import *
from config import *
from table_matrix import *
from queries import *

app = Flask(__name__)

app.config['MYSQL_HOST'] = db_host
app.config['MYSQL_USER'] = db_user
app.config['MYSQL_PASSWORD'] = db_pass
app.config['MYSQL_DB'] = db_database
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#function for checking if the user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:  #if logged in return logged in status
            return f(*args, **kwargs)

        else:   #if not logged in and trying to access a webpage redirect to login
            flash('Unauthorized, Please login','danger')
            return redirect(url_for('login'))
    return wrap

#INDEX ROUTE
@app.route('/')
def index():
    return render_template('index.html', nav_page="home")

#Quick function that will check the users db if the email or username is already taken
def registration_validation(uname, uemail):
    cur = mysql.connection.cursor()
    results = cur.execute("SELECT * FROM users WHERE uname = %s OR uemail = %s", (uname, uemail))
    cur.close()
    if results >= 1:
        return False
    else:
        return True

@app.route('/register', methods=['GET','POST'])
def register():
#form = RegisterForm(request.form)
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        print(password)
        print(confirm)
        v = validateRegistration(name, username, email, password, confirm)

        if v == "Success":
            passw = sha256_crypt.encrypt(password)
            if registration_validation(username, email) is True:
                    #Create a cursor
                cur = mysql.connection.cursor()
                    #Execute register query
                cur.execute("INSERT INTO users(name, uname, uemail, upass) VALUES(%s, %s, %s, %s)",(name, username, email, passw))

                mysql.connection.commit()

                cur.close()

                flash('You are now registered and can login','success')
                print("redirecting")
                return redirect(url_for('login'))

            else: 
                return render_template('register.html', error="Error email or username already used")

        else:
            return render_template('register.html', error=v)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        if SQL_SYNTAX_CHECK(username) is True:
            cur = mysql.connection.cursor()

            result = cur.execute("SELECT * FROM users WHERE uname = %s", [username])

            if result > 0:
                data = cur.fetchone()
                password = data['upass']

                if sha256_crypt.verify(password_candidate, password):
                    session['logged_in'] = True
                    session['username'] = username

                    flash('You are now logged in','success')
                    return redirect(url_for('dashboard'))

        return render_template('login.html', error="Invalid login")

    return render_template('login.html')

@app.route('/logout')
#@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html', nav_page="dashboard")

#Quick function that will check the users db if the email or username is already taken
def random_url_check(shortened):
    cur = mysql.connection.cursor()
    results = cur.execute("SELECT * FROM urltable WHERE url_shortened = \"shortened\";")
    cur.close()
    if results >= 1:
        return False
    else:
        return True

@app.route('/create_link', methods=['GET', 'POST'])
@is_logged_in
def create_link():
    form = CreateUrlForm(request.form)
    if request.method == "POST":
        url_main = request.form.get('url_main')
        if SQL_SYNTAX_CHECK(url_main) is True and len(url_main) >5:

            if validate_link(url_main) is True:
                r_check = 0
                short =""
                while (r_check < 1):
                    shortened = generate_link()
                    if random_url_check(shortened) is True:
                        short = shortened
                        r_check +=1

                cur = mysql.connection.cursor()
                query = create_short_url_query(url_main, short, session.get('username'))
                cur.execute(query)
                mysql.connection.commit()
                cur.close()

                return redirect(url_for('new_link', short_link=short))   

            else:
                return render_template('create_link.html',form=form,nav_page="my_urls",error="Error link provided is invalid")            
        else:
            return render_template('create_link.html', form=form, nav_page="my_urls", error="Error invalid or blank link")
    return render_template('create_link.html',form=form, nav_page="my_urls")

#Page that displays a link to the shorted url
@app.route('/new_link/<string:short_link>', methods=['GET'])
def new_link(short_link):

    return render_template('new_link.html', link=short_link)

#Page that handles incoming shortened links
@app.route('/l/<link>')
def l(link):
    if SQL_SYNTAX_CHECK(link) is True:
        cur = mysql.connection.cursor()
        query = url_query(link)
        results = cur.execute(query)
        
        if results > 0:
            data = cur.fetchone()
            main_url = data['url_long']
            return redirect(main_url)

    return redirect(url_for('l_notfound'))

#Page displayed if a shortened link is not found
@app.route('/l_notfound')
def l_notfound():
    return render_template('l_notfound.html')

@app.route('/view_links')
@is_logged_in
def view_links():
    cur = mysql.connection.cursor()
    username = session.get('username')
    results = cur.execute(f"SELECT * FROM urltable WHERE url_user = \"{username}\";")
    if results > 0:
        tdata = []
        for x in range(0,results):
            data = cur.fetchone()
            tdata.append(data)
            x+=1
        
        matrix = build_links_matrix(results, tdata)

        return render_template('view_links.html',table="true", header_len=len(matrix[0]), rows_len=len(matrix[1]), row_len=len(matrix[1][0]), 
        rows=matrix[1],header=matrix[0], nav_page="my_urls")

    return render_template('view_links.html', nav_page="my_urls")

@app.route('/manage_account')
@is_logged_in
def manage_account():
    username = session.get('username')
    query = create_manage_info_query(username)
    cur = mysql.connection.cursor()
    results = cur.execute(query)
    if results > 0:
        data = cur.fetchone()
        email = data['uemail']
        return render_template('manage_account.html', email=email)
    else:
        return redirect(url_for('index', error="Uknown error occured user not found"))

@app.route('/change_pass', methods=['GET','POST'])
@is_logged_in
def change_pass():
    form = ChangePassword(request.form)
    if request.method == 'POST':
        
        old_password = (form.old_password.data)
        
        passwrd = (form.new_password.data)
        new_password = sha256_crypt.hash(str(passwrd))
        confirm = (form.confirm.data)

        print(f"Passwrd:{passwrd}\nConf:{confirm}")
        if passwrd == confirm:
            print("validated")
            cur = mysql.connection.cursor()
            results = cur.execute(f"SELECT * FROM users WHERE uname = \"{session.get('username')}\";")
            
            if results > 0:
                data = cur.fetchone()
                cur.close()
                passw = data['upass']
                #If old pass equals the one inputed change pass to new pass
                if sha256_crypt.verify(old_password, passw):
                    print("Success Match")
                    cur = mysql.connection.cursor()
                    cur.execute(f"UPDATE users SET upass = \"{new_password}\" WHERE uname = \"{session.get('username')}\"")
                    mysql.connection.commit()

                    cur.close()
                    flash('Succesfuly changed password','success')
                    return redirect(url_for('logout'))
                else:
                    return render_template('change_pass.html', error='Invalid Password')
            #If username is not found in database logout
            else:
                return redirect(url_for('logout'))
        else:
            render_template('change_pass.html', form=form, error="Error Passwords do not Match")

            
    return render_template('change_pass.html', form=form)

if __name__ == '__main__':
    app.secret_key = secret_key
    app.run(debug=True)