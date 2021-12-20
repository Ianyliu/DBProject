from io import SEEK_CUR
from flask import Flask, request, session, redirect, url_for, render_template
from datetime import datetime
from werkzeug.datastructures import MultiDict
from flaskext.mysql import MySQL
import pymysql
import re
import yaml

app = Flask(__name__)
mysql = MySQL()
db = yaml.safe_load(open('db.yaml'))

print(db)

app.config['MYSQL_DATABASE_HOST'] = db['mysql_host']
app.config['MYSQL_DATABASE_USER'] = db['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DATABASE_DB'] = db['mysql_db']

mysql.init_app(app)

# change this to your secret key
# (can be anything, it's for extra protection)
app.secret_key = "feitian"

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users


@app.route("/")
def home():
    # check if user is loggedin
    if "loggedin" in session:
        # user is loggedin show them the home page
        return render_template("home.html", username=session["Username"])

    # user is not loggedin redirect to login page
    return redirect(url_for("login"))


# http://localhost:5000/login/ - this will be the login page
@app.route("/login/", methods=["GET", "POST"])
def login():

    # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # output message if something goes wrong...
    msg = ""

    # check if "username" and "password" POST requests exist (user submitted form)
    if (request.method == "POST"
        and "username" in request.form
            and "password" in request.form):

        # create variables for easy access
        username = request.form["username"]
        password = request.form["password"]

        # check if account exists using MySQL
        cursor.execute(
            "SELECT * FROM Accounts WHERE Username = %s AND Password = %s",
            (username, password),
        )

        # fetch one record and return result
        account = cursor.fetchone()

        # if account exists in accounts table in out database
        if account:
            # create session data, we can access this data in other routes
            session["loggedin"] = True
            session["AccNumber"] = account["AccNumber"]
            session["Username"] = account["Username"]
            session["FirstName"] = account["FirstName"]
            session["LastName"] = account["LastName"]
            session['Role'] = account["Role"]

            # redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for("home"))

        else:
            # account doesnt exist or username/password incorrect
            msg = "Incorrect username/password!"

    return render_template("index.html", msg=msg)


# http://localhost:5000/register - this will be the registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # output message if something goes wrong...
    msg = ""
    # check if "username", "password" and "email" POST requests exist (user submitted form)
    if (request.method == "POST"
        and "username" in request.form
        and "password" in request.form
            and "email" in request.form):

        # create variables for easy access
        FirstName = request.form["FirstName"]
        LastName = request.form["LastName"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        userRole = "Customer"
        now = datetime.now()
        accDate = str(now.strftime("%Y-%m-%d %H:%M:%S"))
        print(accDate)

        # check if account exists using MySQL
        cursor.execute(
            "SELECT * FROM Accounts WHERE Username = %s OR Email = %s;", (username, email))
        account = cursor.fetchone()
        print(account)

        cursor.execute("SELECT MAX(AccNumber) FROM Accounts")
        AccNum = cursor.fetchone()
        NewAccNum = str(AccNum["MAX(AccNumber)"] + 1)

        # if account exists show error and validation checks
        if account:
            msg = "Account already exists!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers!"
        elif not username or not password or not email:
            msg = "Please fill out the form!"
        else:
            Query = ("INSERT INTO Accounts (AccNumber, AccCreateDate, Username, Password, Email, FirstName, LastName, Role, DateModified, CreatedByUser)"
                     f" VALUES ({NewAccNum}, '{accDate}', '{username}', '{password}', '{email}', '{FirstName}', '{LastName}', '{userRole}', NULL, '{username}');")
            print(Query)
            cursor.execute(Query)

            conn.commit()
            msg = "You have successfully registered!"

    elif request.method == "POST":
        # form is empty... (no POST data)
        msg = "Please fill out the form!"

    # show registration form with message (if any)
    return render_template("register.html", msg=msg)

# # http://localhost:5000/editUser - this will be the edit user page
@app.route("/editUser/<requsername>", methods=["GET", "POST"])
def editUser(requsername):
    print(request.method)
    # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # output message if something goes wrong...
    msg = ""

    if "loggedin" not in session or requsername is None:
        return redirect(url_for("home"))

    if request.method == 'GET': 
        Query = (f"SELECT * FROM Accounts WHERE Username = {requsername};")
        cursor.execute(Query)
        userData = cursor.fetchone()
        if session['Role'] == "Manager":
            if userData['Role'] == "Customer": 
                Query = ("SELECT * FROM Accounts, CustomerData, Contact, Lives " +
                f"WHERE Username = {requsername} AND Accounts.AccNumber = CustomerData.AccNumber " + 
                "AND CustomerData.AccNumber = Contact.AccNumber AND CustomerData.AccNumber = Lives.AccNumber;")
                print(Query)
                cursor.execute(Query)
                userData = cursor.fetchone()
                Query = (f"SELECT * FROM CustomerHas WHERE AccNumber = {userData.AccNumber};")
                print(Query)
                cursor.execute(Query)
                creditData = cursor.fetchall()
                print(userData)
                
                return render_template("editCustomer.html", userData=userData, creditData=creditData, role=session['Role'])
            else: 
                Query = (f"SELECT * FROM Accounts, Employee, Contact, Lives " +
                f"WHERE Username = {requsername} AND Accounts.AccNumber = Employee.AccNumber " + 
                "AND Accounts.AccNumber = Contact.AccNumber AND Accounts.AccNumber = Lives.AccNumber;")
                print(Query)
                cursor.execute(Query)
                userData = cursor.fetchone()
                print(userData)
                return render_template("editEmployee.html", userData=userData, role=session['Role'])
        elif session['Role'] == 'CustRep':
            if userData['Role'] == "Customer": 
                Query = (f"SELECT * FROM Accounts, CustomerData, Contact, Lives " +
                f"WHERE Username = {requsername} AND Accounts.AccNumber = CustomerData.AccNumber " + 
                "AND CustomerData.AccNumber = Contact.AccNumber AND CustomerData.AccNumber = Lives.AccNumber;")
                print(Query)
                cursor.execute(Query)
                userData = cursor.fetchone()
                Query = (f"SELECT * FROM CustomerHas WHERE AccNumber = {userData.AccNumber};")
                print(Query)
                cursor.execute(Query)
                creditData = cursor.fetchall()
                return render_template("editCustomer.html", userData=userData, creditData=creditData, role=session['Role'])
            else:
                return redirect(url_for("userManagement"))

    elif request.method == "POST":
        pass

    else:
        return redirect(url_for("home"))


# http://localhost:5000/userManagement - this will be the edit user page
@app.route("/userManagement/", methods=["GET", "POST"])
def manageUsers():

    # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # output message if something goes wrong...
    msg = ""

    if "loggedin" not in session:
        return redirect(url_for("home"))

    if session['Role'] == "Manager":
        # check if "username" and "password" POST requests exist (user submitted form)
        if request.method == "GET":
            EmployeeQuery = ("SELECT Employee.AccNumber, SSN, StartDate,HourlyRate, AccCreateDate, Username, AccEmail, EmailAddress, FirstName, LastName, Accounts.Role, CreatedByUser, DateModified, Telephone "
                             + "FROM databaseproject.Employee "
                             + "LEFT JOIN databaseproject.Accounts ON Accounts.AccNumber = Employee.AccNumber "
                             + "LEFT JOIN databaseproject.Contact ON Contact.AccNumber = Employee.AccNumber;")
            cursor.execute(EmployeeQuery)
            empData = cursor.fetchall()
            print(type(empData))
            print(empData[0])

            CustomerQuery = ("SELECT * FROM CustomerData " +
                             "LEFT JOIN Accounts ON Accounts.AccNumber = CustomerData.AccNumber " +
                             "LEFT JOIN Contact ON Contact.AccNumber = CustomerData.AccNumber;")
            cursor.execute(CustomerQuery)
            custData = cursor.fetchall()
            print(custData)
            print(custData[0])

            return render_template("userManagement.html", empData=empData, custData=custData, role=session['Role'])

        elif request.method == "POST":
            # imd = request.form.to_dict(flat=False)
            user = request.form['editUser']
            print(user)
            session['editUser'] = user

            return redirect(url_for("editUser", requsername=user))
        else:
            pass
    elif session['Role'] == 'CustRep':
        if request.method == "GET":
            CustomerQuery = ("SELECT * FROM CustomerData " +
                             "LEFT JOIN Accounts ON Accounts.AccNumber = CustomerData.AccNumber " +
                             "LEFT JOIN Contact ON Contact.AccNumber = CustomerData.AccNumber;")
            custData = cursor.fetchone()

            EmployeeQuery = ("SELECT Employee.AccNumber, StartDate, AccCreateDate, Username, EmailAddress, FirstName, LastName, Accounts.Role, CreatedByUser, DateModified, Telephone "
                             + "FROM databaseproject.Employee "
                             + "LEFT JOIN databaseproject.Accounts ON Accounts.AccNumber = Employee.AccNumber "
                             + "LEFT JOIN databaseproject.Contact ON Contact.AccNumber = Employee.AccNumber;")
            empData = cursor.fetchone()
            return render_template("editCustomer.html", empData=empData, custData=custData, role=session['Role'], username=session['Username'])

        elif request.method == "POST":
            user = request.form['editUser']
            print(user)
            session['editUser'] = user
            return redirect(url_for("editUser", requsername=user))
        else:
            pass
    else:
        return redirect(url_for("home"))


# http://localhost:5000/Flights - this will be the flights page
@app.route("/Flights/", methods=["GET", "POST"])
def Flights():

    # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # output message if something goes wrong...
    msg = ""

    if "loggedin" not in session:
        return redirect(url_for("home"))

    if session['Role'] == "Manager":
        # check if "username" and "password" POST requests exist (user submitted form)
        if request.method == "GET":
            Query = ("SELECT * FROM Flights " + 
            "LEFT JOIN FlightFares ON FlightFares.FLNO = Flights.FLNO " + 
            "LEFT JOIN OperatedBy ON OperatedBy.FLNO = Flights.FLNO " + 
            "LEFT JOIN Airlines ON OperatedBy.ALID  = Airlines.ALID " +
            "LEFT JOIN StopsAt ON StopsAt.FLNO = Flights.FLNO;")
            print(Query)
            cursor.execute(Query)
            Data = cursor.fetchall()
            print(Data)

            return render_template("Flights.html", Data=Data, role=session['Role'], username=session['Username'])

        elif request.method == "POST":
            # imd = request.form.to_dict(flat=False)
            user = request.form['editUser']
            print(user)
            session['editUser'] = user

            return redirect(url_for("editUser"))
        else:
            pass
    elif session['Role'] == 'CustRep':
        if request.method == "GET":
            CustomerQuery = ("SELECT * FROM CustomerData " +
                             "LEFT JOIN Accounts ON Accounts.AccNumber = CustomerData.AccNumber " +
                             "LEFT JOIN Contact ON Contact.AccNumber = CustomerData.AccNumber;")
            custData = cursor.fetchone()

            EmployeeQuery = ("SELECT Employee.AccNumber, StartDate, AccCreateDate, Username, EmailAddress, FirstName, LastName, Accounts.Role, CreatedByUser, DateModified, Telephone "
                             + "FROM databaseproject.Employee "
                             + "LEFT JOIN databaseproject.Accounts ON Accounts.AccNumber = Employee.AccNumber "
                             + "LEFT JOIN databaseproject.Contact ON Contact.AccNumber = Employee.AccNumber;")
            empData = cursor.fetchone()
            return render_template("editCustomer.html", empData=empData, custData=custData, role=session['Role'], username=session['Username'])

        elif request.method == "POST":
            user = request.form['editUser']
            print(user)
            session['editUser'] = user
            return redirect(url_for("editUser"))
        else:
            pass
    else:
        return redirect(url_for("home"))

# http://localhost:5000/logout - this will be the logout page


@app.route("/logout")
def logout():
    # remove session data, this will log the user out
    session.pop("loggedin", None)
    session.pop("AccNumber", None)
    session.pop("username", None)

    # redirect to login page
    return redirect(url_for("login"))


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route("/profile")
def profile():
    # check if account exists using MySQL
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # check if user is loggedin
    if "loggedin" in session:
        # we need all the account info for the user so we can display it on the profile page
        cursor.execute(
            "SELECT * FROM Accounts WHERE AccNumber = %s", [session["AccNumber"]])
        account = cursor.fetchone()

        # show the profile page with account info
        return render_template("profile.html", account=account)

    # user is not loggedin redirect to login page
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
