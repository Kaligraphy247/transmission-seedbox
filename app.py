from flask import Flask, send_from_directory, render_template, url_for, request, send_file, redirect
from dotenv import load_dotenv
from datetime import datetime as dt
import os, time, subprocess, shutil

load_dotenv()
DOWNLOAD_FOLDER = os.environ.get("DOWNLOAD_FOLDER")
TEMP_UPLOAD_FOLDER = os.environ.get("TEMP_UPLOAD_FOLDER")
ALLOWED_FILES = os.environ.get("ALLOWED_FILES")
ALLOWED_FILES = tuple(ALLOWED_FILES)
app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = DOWNLOAD_FOLDER

# error handlers
# app.register_error_handler(500, error_500)

# @app.errorhandler(500)
# def error_500(e):
# 	'''Internal server error handler'''
# 	return "Error 500, nothing much to tell you at this point", 500

@app.route("/")
@app.route("/index")
def index():
	all_files_info = []
	# test
	download = app.config["UPLOAD_FOLDER"]
	folders = []
	files = os.listdir(app.config["UPLOAD_FOLDER"]) # files in current directory

	# same as above, used exclusively for each file's name folders are ignored
	file_name = [file for file in files if file.endswith(ALLOWED_FILES)]
	for file in files:
		if os.path.isdir(f"{app.config['UPLOAD_FOLDER']}/{file}"):
			folders.append(file)


	# The complex list comprehension below generates a list of the file sizes
	#  already converted to megabytes (mb)
	file_size = [os.stat((f"{app.config['UPLOAD_FOLDER']}/{file}")) for file in files]
	file_size = [round(file.st_size / (1024 * 1024), 3) for file in file_size] # converts to mb and rounds to 3 decimal places

	# This complex list comprehension below generates a list of the file's timestamp
	# converted parsed in strftime
	created_at = [os.stat(f"{app.config['UPLOAD_FOLDER']}/{file}").st_mtime for file in files]
	created_at = [dt.strftime(dt.fromtimestamp(mtime), "%Y-%m-%d %H:%M:%S") for mtime in created_at]

	
	for name, folder, timestamp, size in zip(files, folders, created_at, file_size):
		all_files_info.extend([[name, folder, timestamp, size]])
	return render_template("index.html", files=all_files_info, root=download)




@app.route("/download")
def download_page():
	files = os.listdir(app.config["UPLOAD_FOLDER"])
	return render_template("download.html", files=files)


# @app.route("/download/<path:filename>")
# def download2(filename):
# 	uploads = app.config["UPLOAD_FOLDER"]
# 	print(uploads)
# 	return send_file(filename, as_attachment=True)


@app.route("/download/<path:filename>")
def download(filename):
	filename = os.path.abspath(filename)
	return send_file(filename, as_attachment=True)
	# return send_from_directory(uploads, path=filename, as_attachment=True)#, as_attachment=True


@app.route("/upload", methods=["GET", "POST"])
def upload():
	if request.method == "POST":
		file = request.files['file']
		url = request.form.get('url')

		if file != '':
			temp_file = f"{os.path.join(TEMP_UPLOAD_FOLDER)}/{file.filename}"
			# temp_file = f"data/uploads/{file.filename}"
			print(temp_file)
			file.save(temp_file)
			time.sleep(5) # wait 5 seconds after file is saved? an add torrent
			subprocess.Popen(f"sudo transmission-remote -n 'transmission:transmission' -a {temp_file}", shell=True)
			time.sleep(60) # wait, 1 minute and then clear .torrent file
			os.remove(temp_file)
			print(f"deleted torrent file: {temp_file}")


			# subprocess.Popen(f'echo {file.filename}', shell=True) # debug
			# subprocess.Popen(f"sudo transmission-remote -n 'transmission:transmission' -a '{file}'", shell=True)
		elif url != '':
			# subprocess.Popen(f'echo {url}', shell=True) # debug
			subprocess.Popen(f"sudo transmission-remote -n 'transmission:transmission' -a '{url}'", shell=True)
		# print(file.filename, url)
	return render_template('upload.html')


@app.route('/folder')
def folder_view():
	# lambda function to convert size to mb only
	to_mb = lambda size: round(size / (1024 * 1024), 2)

	# lambda function to convert secs since unix epoch
	created_at = lambda secs_since_unix_epoch: dt.strftime(
			dt.fromtimestamp(secs_since_unix_epoch), "%Y-%m-%d %H:%M:%S")
	
	dirs = os.scandir()
	return render_template("folderv2.html", dirs=dirs, to_mb=to_mb, timestamp=created_at, os=os, len=len, cwd=os.getcwd())


@app.route('/cd')
def cd():
	try:
		os.chdir(request.args.get('path'))
	except PermissionError:
		return "You do not have persmission to view this folder or file"
	return redirect('/folder')


@app.route('/md')
def md():
    # create new folder
    new_folder = request.args.get('folder')
    try:
        os.mkdir(new_folder)
    except FileExistsError:
        return "Folder or file already exists"
    # redirect to file manager
    return redirect('/folder')


@app.route('/rm')
def rm():
    # create new folder
    folder = request.args.get('dir')
    try:
        os.rmdir(folder) # only empty folders
    except OSError:
        return """folder is not empty, please check before deleting""" # or <a href="force-rm?dir=dir">Here</a> to force delete"""
    # shutil.rmtree(folder) # delete folders recursively

    # redirect to file manager
    return redirect('/folder')


@app.route('/force-rm')
def force_rm():
    # create new folder
    folder = request.args.get('dir')
    # try:
    #     os.rmdir(folder) # only empty folders
    # except OSError:
    #     return """folder is not empty, please check before deleting or <a href="https://www.google.com">Here</a> to force delete"""
    shutil.rmtree(folder) # delete folders recursively

    # redirect to file manager
    return redirect('/folder')


@app.route('/view')
def view():
    # content = subprocess.check_output(f"bat {request.args.get('file')}")
    # get the file content
    with open(request.args.get('file'), 'r',) as file:
        return file.read().replace('\n', '<br>')


@app.route('/rm-file')
def rm_file():
    # file = os.remove(request.args.get('file'))
    file = "to be deleted"
    print("Deleted ", file)
    return redirect('/folder')


@app.route('/view-img')
def view_img():
    img = "an image"

    print("Deleted ",)
    return redirect('/folder')




if __name__ == "__main__":
	app.run(use_reloader=True, debug=True)