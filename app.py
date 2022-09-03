from flask import Flask, send_from_directory, render_template, url_for
import os
app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = "data"




@app.route("/")
def index():
    return "it's working"

@app.route("/download")
def download_page():
	files = os.listdir(app.config["UPLOAD_FOLDER"])
	return render_template("download.html", files=files)


@app.route("/download/<path:filename>")
def download(filename):
	uploads = app.config["UPLOAD_FOLDER"]
	print(uploads)
	return send_from_directory(uploads, path=filename, as_attachment=True)#, as_attachment=True



if __name__ == "__main__":
	app.run(use_reloader=True, debug=True)