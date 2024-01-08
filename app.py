import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_security import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
import mysql.connector

# KONEKCIJA SA BAZOM 
konekcija = mysql.connector.connect(
 passwd="", 
 user="root", 
 database="sus", 
 port=3306, 
 auth_plugin='mysql_native_password'  
)
kursor = konekcija.cursor(dictionary=True)

# DEFINISANJE APLIKACIJE
app = Flask(__name__) 
app.secret_key = "SISTEMZASKLADISTENJESUS"
login_manager = LoginManager()
login_manager.init_app(app)

# DEKLARACIJA UPLOAD FOLDERA
UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# KORISNE FUNKCIJE
def vrati_korisnika(email):
	upit = "SELECT * FROM user WHERE email = %s"
	vrednosti = (email,)
	kursor.execute(upit, vrednosti)
	user = kursor.fetchone()
	return user

def sacuvaj_sliku(forma):
	naziv_slike = ""
	if "slika" in request.files:
		file = request.files["slika"]
		if file.filename:
			naziv_slike = forma["id"] + file.filename 
			file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
			return naziv_slike

# KREIRANJE KLASE USER
class User(UserMixin):
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = role

@login_manager.user_loader
def load_user(user_id):
	upit = "SELECT id, role FROM user WHERE id = %s"
	vrednosti = (user_id,)
	kursor.execute(upit, vrednosti)
	user = kursor.fetchone()
	if user:
		return User(user["id"], user["role"])
	return None


# LOGIKA APLIKACIJE - RUTE

@app.route('/')
def index():
	return render_template('base.html')

@app.route('/login', methods = ["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template('login.html', page='login')
	elif request.method == "POST":
		forma = request.form
		user = vrati_korisnika(forma["email"])
		if user:
			print(check_password_hash(user["lozinka"], forma['lozinka']))
			if check_password_hash(user["lozinka"], forma['lozinka']):
				user_obj = User(user["id"], user["role"])
				login_user(user_obj)
				flash("Uspešno ste se ulogvali!", 'success')
				if current_user.is_authenticated and current_user.role == 'Administrator':
					return redirect(url_for("users"))
				else:
					return redirect(url_for("skladista"))
			else:
				flash("Pogrešna lozinka", 'danger')
				return redirect(url_for("login"))
		else: 
			flash("Ne postoji korisnik s ovim nalogom", 'danger')
			return redirect(url_for("login"))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) 

@app.route('/users')
@login_required
def users():
	if current_user.is_authenticated and current_user.role == 'Administrator':
		upit = "select * from user"
		kursor.execute(upit)
		users = kursor.fetchall()
		return render_template('users.html', users=users)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))
	

@app.route('/newuser', methods=["GET", "POST"])
@login_required
def newuser():
	if current_user.is_authenticated and current_user.role == 'Administrator':
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
			forma["role"],
			)
			upit = """ INSERT INTO 
				user(ime,prezime,email,lozinka,role)
				VALUES (%s, %s, %s, %s, %s) 
				"""
			kursor.execute(upit, vrednosti)
			konekcija.commit()
			return redirect(url_for("users"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))



@app.route('/edituser/<id>', methods=["GET", "POST"])
@login_required
def edituser(id):
	if current_user.is_authenticated and current_user.role == 'Administrator':
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
			forma["role"],
			id,
			)
			upit = """ UPDATE user SET
				ime = %s,
				prezime = %s,
				email = %s,
				lozinka = %s,
				role = %s
				WHERE id = %s
			"""
			kursor.execute(upit, vrednosti)
			konekcija.commit()
			return redirect(url_for("users"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))
		

@app.route('/deleteuser/<id>', methods=["POST"])
@login_required
def deleteuser(id):
	if current_user.is_authenticated and current_user.role == 'Administrator':
		upit = """
		DELETE FROM user WHERE id=%s
		"""
		vrednost = (id,)
		kursor.execute(upit, vrednost)
		konekcija.commit()
		return redirect(url_for("users"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))
	

@app.route('/proizvodilager')
@login_required
def proizvodilager():
	print(current_user.role)
	proizvod = "PROIZVOD"
	if current_user.is_authenticated and (current_user.role == 'Zaposleni' or current_user.role == 'Menadzer'):
		flash("Uspešno ste pristupili stranici proizvoda na lageru", 'success')
		return render_template('proizvodilager.html', proizvod=proizvod)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))

@app.route('/editproizvod/<id>', methods=["GET", "POST"])
@login_required
def editproizvod(id):
    if current_user.is_authenticated and current_user.role == 'Menadzer':
        if request.method == "GET":
            upit = "SELECT * FROM proizvod WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            proizvod = kursor.fetchone()
            return render_template("editproizvod.html", proizvod=proizvod)
        elif request.method == "POST":
            forma = request.form
            naziv_slike = ""

            if "slika" in request.files:
                kursor.execute("SELECT * FROM proizvod where id=%s", (id,))
                rezultat = kursor.fetchone()
                naziv_slike = rezultat["slika"]

                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["naziv"] + file.filename 
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))

            vrednosti = (
                forma["naziv"],
                forma["kategorija"],
                forma["cena"],
                naziv_slike,
                id,
            )
            upit = """ UPDATE proizvod SET
                naziv = %s,
                kategorija = %s,
                cena = %s,
                slika = %s
                WHERE id = %s
            """
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            flash('Uspešno ste izmenili proizvod!', 'success')
            return redirect(url_for("dostupniproizvodi"))
    else:
        flash("Niste ovlašćeni da pristupite stranici", 'danger')
        return redirect(url_for("login"))
	

@app.route('/deleteproizvod/<id>', methods=["POST"])
@login_required
def deleteproizvod(id):
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		upit = """
		DELETE FROM proizvod WHERE id=%s
		"""
		vrednost = (id,)
		kursor.execute(upit, vrednost)
		konekcija.commit()
		flash("Uspešno ste obrisali proizvod", "success")
		return redirect(url_for("dostupniproizvodi"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))


@app.route('/newproizvod', methods=["GET", "POST"])
@login_required
def newproizvod():
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		if request.method == "GET":
			return render_template('newproizvod.html')
		elif request.method == "POST":
			forma = request.form
			naziv_slike = ""
			if "slika" in request.files:
				file = request.files["slika"]
				if file.filename:
					naziv_slike = forma["naziv"] + file.filename 
					file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
			vrednosti = (
			forma["naziv"],
			forma["kategorija"],
			forma["cena"],
			naziv_slike
			)
			upit = """ INSERT INTO 
				proizvod(naziv,kategorija,cena,slika)
				VALUES (%s, %s, %s, %s) 
				"""
			kursor.execute(upit, vrednosti)
			konekcija.commit()
			flash('Uspešno kreiran proizvod!', 'success')
			return redirect(url_for("dostupniproizvodi"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))

@app.route('/dostupniproizvodi', methods=["GET"])
@login_required
def dostupniproizvodi():
	if current_user.is_authenticated and (current_user.role == 'Zaposleni' or current_user.role == 'Menadzer'):
		if request.method == "GET":
				upit = "select * from proizvod"
				kursor.execute(upit)
				proizvod = kursor.fetchall()
				return render_template('dostupniproizvodi.html', proizvod=proizvod)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))

@app.route('/poruciproizvod')
@login_required
def poruciproizvod():
	return render_template('poruciproizvod.html')

@app.route('/isporuciproizvod')
@login_required
def isporuciproizvod():
	return render_template('isporuciproizvod.html')

@app.route('/skladista')
@login_required
def skladista():
	return render_template('skladista.html', page='skladista')

@app.route('/editskladiste')
@login_required
def editskladiste():
	return render_template('editskladiste.html')

@app.route('/newskladiste')
@login_required
def newskladiste():
	return render_template('newskladiste.html')

@app.route('/popunjenost')
@login_required
def popunjenost():
	return render_template('popunjenost.html')

app.run(debug =True) #pokretanje aplikacije

