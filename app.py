import os, re
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_security import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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
	return redirect(url_for("login"))

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
# @login_required
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
			flash("Uspešno ste kreirali novog korisnika", "success")
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
			flash("Uspešno ste izmenili korisnika", "success")
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
		flash("Uspešno ste izbrisali korisnika!", "success")
		return redirect(url_for("users"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))
	

@app.route('/proizvodilager/<sid>')
@login_required
def proizvodilager(sid):
	if current_user.is_authenticated and (current_user.role == 'Zaposleni' or current_user.role == 'Menadzer'):
		if request.method == "GET":
				upit = upit = """
    						SELECT proizvod.*, skladisteproizvod.kolicina
							FROM proizvod
							INNER JOIN skladisteproizvod ON proizvod.id = skladisteproizvod.proizvod_id
							WHERE skladisteproizvod.skladiste_id = %s AND skladisteproizvod.kolicina  > 0;
						"""
				vrednosti = (sid,)
				kursor.execute(upit, vrednosti)
				proizvod = kursor.fetchall()
				print(proizvod)
		return render_template('proizvodilager.html', proizvod=proizvod, sid=sid)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))

@app.route('/editproizvod/<id>/<sid>', methods=["GET", "POST"])
@login_required
def editproizvod(id, sid):
    if current_user.is_authenticated and current_user.role == 'Menadzer':
        if request.method == "GET":
            upit = "SELECT * FROM proizvod WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            proizvod = kursor.fetchone()
            return render_template("editproizvod.html", proizvod=proizvod, sid=sid)
        elif request.method == "POST":
            forma = request.form
            naziv_slike = ""

            if "slika" in request.files:
                kursor.execute("SELECT * FROM proizvod where id=%s", (id,))
                rezultat = kursor.fetchone()
                naziv_slike = rezultat["slika"]

                file = request.files["slika"]
                if file.filename:
                    naziv_slike = re.sub(r'[^\w.-]', '', forma["naziv"]) + secure_filename(file.filename)
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
            return redirect(url_for("dostupniproizvodi", sid=sid))
    else:
        flash("Niste ovlašćeni da pristupite stranici", 'danger')
        return redirect(url_for("login"))
	

@app.route('/deleteproizvod/<id>/<sid>', methods=["POST"])
@login_required
def deleteproizvod(id, sid):
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		upit = """
		DELETE FROM proizvod WHERE id=%s
		"""
		vrednost = (id,)
		kursor.execute(upit, vrednost)
		konekcija.commit()
		flash("Uspešno ste obrisali proizvod", "success")
		return redirect(url_for("dostupniproizvodi", sid=sid))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))


@app.route('/newproizvod/<sid>', methods=["GET", "POST"])
@login_required
def newproizvod(sid):
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		if request.method == "GET":
			return render_template('newproizvod.html', sid=sid)
		elif request.method == "POST":
			forma = request.form
			naziv_slike = ""
			if "slika" in request.files:
				file = request.files["slika"]
				if file.filename:
					naziv_slike = re.sub(r'[^\w.-]', '', forma["naziv"]) + secure_filename(file.filename)
					os.makedirs(UPLOAD_FOLDER, exist_ok=True)
					file.save(os.path.join(UPLOAD_FOLDER, naziv_slike))
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
			return redirect(url_for("dostupniproizvodi", sid=sid))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))

@app.route('/dostupniproizvodi/<sid>', methods=["GET"])
@login_required
def dostupniproizvodi(sid):
	if current_user.is_authenticated and (current_user.role == 'Menadzer'):
		if request.method == "GET":
				upit = "select * from proizvod"
				kursor.execute(upit)
				proizvod = kursor.fetchall()
				return render_template('dostupniproizvodi.html', proizvod=proizvod, sid=sid)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))

@app.route('/poruciproizvod/<sid>/<id>', methods=["GET", "POST"])
@login_required
def poruciproizvod(sid, id):
	if current_user.is_authenticated and (current_user.role == 'Menadzer' or current_user.role== 'Zaposleni'):
		if request.method == "GET":
			upit = "select * from proizvod"
			kursor.execute(upit)
			proizvod = kursor.fetchall()
			print(proizvod, sid, id)
			return render_template('poruciproizvod.html', sid=sid, id=id, proizvod=proizvod)
		elif request.method == "POST":
			forma = request.form 
			vrednosti = (
			sid,
			forma["proizvod"],
			forma["kolicina"]
			)

			upit = """ SELECT skladisteproizvod.*, skladiste.popunjeno, skladiste.kapacitet 
			FROM skladisteproizvod
			INNER JOIN skladiste ON skladisteproizvod.skladiste_id = skladiste.id 
			WHERE skladiste_id=%s and proizvod_id=%s
					"""
			kursor.execute(upit, (sid, forma["proizvod"],))
			rezultat = kursor.fetchone()

			upit = """ SELECT * FROM skladiste where id = %s
					"""
			kursor.execute(upit, (sid,))
			rezultat2 = kursor.fetchone()


			dostupno = int(rezultat2['kapacitet']) - int(rezultat2['popunjeno'])
			if rezultat == None:
				if (int(forma['kolicina']) > dostupno) or (int(forma["kolicina"]) < 0):
					flash("Nepravilan unos količine", "danger")
					return redirect(url_for("proizvodilager", sid=sid))
				else:
					upit = """ INSERT INTO 
						skladisteproizvod(skladiste_id,proizvod_id,kolicina)
						VALUES (%s, %s, %s) 
						"""
					kursor.execute(upit, vrednosti)
					konekcija.commit()
					flash("Uspešno ste stavili na lager nov proizvod", "success")
					return redirect(url_for("proizvodilager", sid=sid))
			else:
				kolicina = int(forma["kolicina"]) + int(rezultat["kolicina"])
				if kolicina > dostupno or kolicina <0:
					flash("Nepravilan unos količine", "danger")
					return redirect(url_for("proizvodilager", sid=sid))
				else:
					vrednosti = (
						kolicina,
						rezultat["id"],
					)
					print(kolicina, rezultat["id"])
					upit = """ UPDATE skladisteproizvod SET
					kolicina = %s
					WHERE id = %s
				"""
					kursor.execute(upit, vrednosti)
					konekcija.commit()
					flash("Uspešno ste poručili novu količinu proizvoda", "success")
					return redirect(url_for("proizvodilager", sid=sid))

	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))


@app.route('/isporuciproizvod/<sid>/<id>', methods=['GET', 'POST'])
@login_required
def isporuciproizvod(sid, id):
	if current_user.is_authenticated and (current_user.role == 'Menadzer' or current_user.role== 'Zaposleni'):
		if request.method == "GET":
			upit = "select * from proizvod"
			kursor.execute(upit)
			proizvod = kursor.fetchall()
			print(proizvod, sid, id)
			return render_template('isporuciproizvod.html', sid=sid, id=id, proizvod=proizvod)
		elif request.method == "POST":
			forma = request.form 
			vrednosti = (
			sid,
			forma["proizvod"],
			forma["kolicina"]
			)

			upit = """ SELECT * FROM skladisteproizvod WHERE skladiste_id=%s and proizvod_id=%s
					"""
			kursor.execute(upit, (sid, forma["proizvod"],))
			rezultat = kursor.fetchone()

			if rezultat == None:
				flash("Došlo je do greške...", "danger")
				return redirect(url_for("proizvodilager", sid=sid))
			else:
				if (int(rezultat["kolicina"]) < int(forma['kolicina'])) or int(forma['kolicina']) < 0:
					flash("Nepravilan unos količine", "danger")
					return redirect(url_for("proizvodilager", sid=sid))
				else: 
					kolicina = int(rezultat["kolicina"]) - int(forma['kolicina'])
					vrednosti = (
						kolicina,
						rezultat["id"],
					)
					print(kolicina, rezultat["id"])
					upit = """ UPDATE skladisteproizvod SET
					kolicina = %s
					WHERE id = %s
				"""
					kursor.execute(upit, vrednosti)
					konekcija.commit()
					flash("Uspešno ste isporučili navedenu količinu proizvoda", "success")
					return redirect(url_for("proizvodilager", sid=sid))

	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))

@app.route('/skladista', methods=["GET", "POST"])
@login_required
def skladista():
	if current_user.is_authenticated and (current_user.role == 'Zaposleni' or current_user.role == 'Menadzer'):
		if request.method == "GET":
				upit = "select * from skladiste"
				kursor.execute(upit)
				skladiste = kursor.fetchall()
		return render_template('skladista.html', skladiste=skladiste)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))

@app.route('/editskladiste/<sid>', methods=["GET", "POST"])
@login_required
def editskladiste(sid):
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		if request.method == "GET":
			upit = "SELECT * FROM skladiste WHERE id=%s"
			vrednost = (sid,)
			kursor.execute(upit, vrednost)
			skladiste = kursor.fetchone()
			return render_template("editskladiste.html", skladiste=skladiste)

		elif request.method == "POST":
			forma = request.form 
			vrednosti = (
			forma["naziv"],
			forma["adresa"],
			forma["kapacitet"],
			sid,
			)
			upit = """ UPDATE skladiste SET
				naziv = %s,
				adresa = %s,
				kapacitet = %s
				WHERE id = %s
			"""
			kursor.execute(upit, vrednosti)
			konekcija.commit()
			flash("Uspešno ste izmenili skladište", "success")
			return redirect(url_for("skladista"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))

@app.route('/newskladiste', methods=["GET", "POST"])
@login_required
def newskladiste():
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		if request.method == "GET":
			return render_template('newskladiste.html')
		elif request.method == "POST":
			forma = request.form
			vrednosti = (
			forma["naziv"],
			forma["adresa"],
			forma["kapacitet"],
			)
			upit = """ INSERT INTO 
				skladiste(naziv,adresa,kapacitet)
				VALUES (%s, %s, %s) 
				"""
			kursor.execute(upit, vrednosti)
			konekcija.commit()
			flash('Uspešno kreirano skladište!', 'success')
			return redirect(url_for("skladista"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for("login"))
	
@app.route('/deleteskladiste/<sid>', methods=["POST"])
@login_required
def deleteskladiste(sid):
	if current_user.is_authenticated and current_user.role == 'Menadzer':
		upit = """
		DELETE FROM skladiste WHERE id=%s
		"""
		vrednost = (sid,)
		kursor.execute(upit, vrednost)
		konekcija.commit()
		flash("Uspešno ste izbrisali skladište!", "success")
		return redirect(url_for("skladista"))
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))

@app.route('/popunjenost/<sid>')
@login_required
def popunjenost(sid):
	if current_user.is_authenticated and (current_user.role == 'Zaposleni' or current_user.role == 'Menadzer'):
		if request.method == "GET":
				upit = "select * from skladiste WHERE id=%s"
				vrednosti = (sid,)
				kursor.execute(upit, vrednosti)
				skladiste = kursor.fetchone()
				procenat = round(skladiste["popunjeno"] / skladiste["kapacitet"] * 100)
				if procenat<76:
					kategorija = "success"
				elif procenat>75 and procenat<90:
					kategorija = "warning"
				else:
					kategorija = "danger"
		return render_template('popunjenost.html', skladiste=skladiste, sid=sid, procenat=procenat, kategorija=kategorija)
	else:
		flash("Niste ovlašćeni da pristupite stranici", 'danger')
		return redirect(url_for('login'))


app.run(debug =True) #pokretanje aplikacije

