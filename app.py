from flask import Flask, render_template, url_for

app = Flask(__name__) #definisanje flaska

@app.route('/')
def index():#definisanje funkcije o ruti index
	return render_template('base.html') #pristupanju fajla

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/users')
def users():
	return render_template('users.html')

@app.route('/newuser')
def newuser():
	return render_template('newuser.html')

@app.route('/edituser')
def edituser():
	return render_template('edituser.html')

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
	return render_template('skladista.html')

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

