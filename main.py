from flask import Flask, abort, render_template

from applications import api

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("startsida.html", stader=api.STADER)


@app.route("/<stad>")
def stad_sida(stad):
    try:
        info = api.hamta_stad(stad)
    except ValueError:
        abort(404)

    try:
        data = api.hamta_prognos(info["lat"], info["lon"])
        dagar = api.tolka_prognos(data)
    except (api.VaderApiFel, ValueError) as e:
        return render_template("stad.html", stad=info, fel=str(e)), 502

    return render_template("stad.html", stad=info, dagar=dagar)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
