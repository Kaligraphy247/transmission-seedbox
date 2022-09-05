from flask import Flask, send_from_directory, render_template, url_for
from dotenv import load_dotenv
# from datetime import datetime as dt
import os, time

load_dotenv()
DOWNLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")


app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = DOWNLOAD_FOLDER




@app.route("/")
def index():
	all_files_info = []
	files = os.listdir(app.config["UPLOAD_FOLDER"]) # files in current directory
	# file_name = files # same as above, used exclusively for each file's name 

	# The complex list comprehension below generates a list of the file sizes
	#  already converted to megabytes (mb)
	file_size = [os.stat((f"{app.config['UPLOAD_FOLDER']}/{file}")) for file in files]
	file_size = [round(file.st_size / (1024 * 1024), 3) for file in file_size] # converts to mb and rounds to 3 decimal places

	# This complex list comprehension below generates a list of the file timstamp
	# converted to gmtime
	created_at = [os.stat(f"{app.config['UPLOAD_FOLDER']}/{file}").st_mtime for file in files]
	created_at = [f"{time.gmtime(mtime).tm_year}.{time.gmtime(mtime).tm_mon}.{time.gmtime(mtime).tm_wday} {time.gmtime(mtime).tm_hour}:{time.gmtime(mtime).tm_min}:{time.gmtime(mtime).tm_sec}" for mtime in created_at]
	
	for name, timestamp, size in zip(files, created_at, file_size):
		all_files_info.extend([[name, timestamp, size]])


	return render_template("index.html", files=all_files_info)

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