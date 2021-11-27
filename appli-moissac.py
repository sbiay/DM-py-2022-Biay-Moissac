from flask import Flask, render_template

app = Flask("Application")


@app.route("/")
@app.route("/templates/css/moissac1.css")
def accueil():
    return render_template("accueil.html", nom="Scriptorium de Moissac")


@app.route("/codices/<int:cod_id>")
def notice_codex(cod_id):
    return "Notice " + str(cod_id) + " du catalogue de Jean Dufour"


app.run()
