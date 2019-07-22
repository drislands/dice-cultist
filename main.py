from flask import render_template
import connexion

cultist = connexion.App(__name__, specification_dir="config")

cultist.add_api("swagger.yml")


@cultist.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    cultist.run(debug=True)
