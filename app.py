from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


konekcija = mysql.connector.connect(
 passwd="", # lozinka za bazu 
 user="root", # korisničko ime
 database="sus", # ime baze
 port=3306, # port na kojem je mysql server
 auth_plugin='mysql_native_password' # ako se koristi mysql 8.x 
)
kursor = konekcija.cursor(dictionary=True)

app = Flask(__name__) #definisanje flaska

@app.route('/')
def index():
	return render_template('base.html')

@app.route('/login')
def login():
	return render_template('login.html', page='login')

@app.route('/users')
def users():
	upit = "select * from user"
	kursor.execute(upit)
	users = kursor.fetchall()
	return render_template('users.html', users=users)

@app.route('/newuser', methods=["GET", "POST"])
def newuser():
	if request.method == "GET":
		return render_template('newuser.html')
	elif request.method == "POST":
		forma = request.form 
		hesovana_lozinka = generate_password_hash(forma["lozinka"])
		vrednosti = (
		forma["ime"],
		forma["prezime"],
		forma["emailNovi"],
		hesovana_lozinka,
		forma["rola"],
		  )
		upit = """ INSERT INTO 
			user(ime,prezime,email,lozinka,rola)
			VALUES (%s, %s, %s, %s, %s) 
			"""
		kursor.execute(upit, vrednosti)
		konekcija.commit()
		return redirect(url_for("users"))






@app.route('/edituser/<id>', methods=["GET", "POST"])
def edituser(id):
	if request.method == "GET":
		upit = "SELECT * FROM user WHERE id=%s"
		vrednost = (id,)
		kursor.execute(upit, vrednost)
		user = kursor.fetchone()
		return render_template("edituser.html", user=user)

	elif request.method == "POST":
		forma = request.form 
		hesovana_lozinka = generate_password_hash(forma["lozinka"])
		vrednosti = (
		forma["ime"],
		forma["prezime"],
		forma["emailNovi"],
		hesovana_lozinka,
		forma["rola"],
		id,
		  )
		upit = """ UPDATE user SET
            ime = %s,
            prezime = %s,
            email = %s,
            lozinka = %s,
            rola = %s
            WHERE id = %s
        """
		kursor.execute(upit, vrednosti)
		konekcija.commit()
		return redirect(url_for("users"))

@app.route('/deleteuser/<id>', methods=["POST"])
def deleteuser(id):
	upit = """
	DELETE FROM user WHERE id=%s
	"""
	vrednost = (id,)
	kursor.execute(upit, vrednost)
	konekcija.commit()
	return redirect(url_for("users"))

	

@app.route('/proizvodilager')
def proizvodilager():
	return render_template('proizvodilager.html')

@app.route('/editproizvod')
def editproizvod():
	return render_template('editproizvod.html')

@app.route('/newproizvod')
def newproizvod():
	return render_template('newproizvod.html')

@app.route('/dostupniproizvodi')
def dostupniproizvodi():
	return render_template('dostupniproizvodi.html')

@app.route('/poruciproizvod')
def poruciproizvod():
	return render_template('poruciproizvod.html')

@app.route('/isporuciproizvod')
def isporuciproizvod():
	return render_template('isporuciproizvod.html')

@app.route('/skladista')
def skladista():
	return render_template('skladista.html', page='skladista')

@app.route('/editskladiste')
def editskladiste():
	return render_template('editskladiste.html')

@app.route('/newskladiste')
def newskladiste():
	return render_template('newskladiste.html')

@app.route('/popunjenost')
def popunjenost():
	return render_template('popunjenost.html')

app.run(debug =True) #pokretanje aplikacije

