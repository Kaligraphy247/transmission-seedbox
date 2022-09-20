from flask import Flask, send_from_directory, render_template, url_for, request
from flask import Flask, send_from_directory, render_template, request, send_file, redirect
from dotenv import load_dotenv
from datetime import datetime as dt
import os, time, subprocess, shutil, math


load_dotenv()
DOWNLOAD_FOLDER = os.environ.get("DOWNLOAD_FOLDER")
TEMP_UPLOAD_FOLDER = os.environ.get("TEMP_UPLOAD_FOLDER")
ALLOWED_FILES = os.environ.get("ALLOWED_FILES")
ALLOWED_FILES = tuple(ALLOWED_FILES) # just to be explicit, it could have been done the first line
app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = DOWNLOAD_FOLDER

# error handlers
## only done, if using blueprints
# app.register_error_handler(404, error404)

@app.errorhandler(404)
def error404(error):
	"""Not Found error, 404"""
	return render_template(template_name_or_list="404.html")
	# return "404 page i guess ☠🤥"

@app.route("/")
@app.route("/index")
def index():
	all_files_info = []
	# os.chdir(f'/{app.config["UPLOAD_FOLDER"]}')
	# os.chdir("/data")
	# print(os.chdir(os.path.abspath("data")))
	# dirs = os.scandir(os.path.abspath(app.config["UPLOAD_FOLDER"]))
	
	return render_template("index.html")# timestamp=created_at)


@app.route("/download")
def download_page():
	files = os.listdir(app.config["UPLOAD_FOLDER"])
	return render_template("download.html", files=files)


@app.route("/download/<path:filename>")
def download(filename):
	filename = os.path.abspath(filename)
	return send_file(filename, as_attachment=True)
	# return send_from_directory(uploads, path=filename, as_attachment=True)#, as_attachment=True


@app.route("/downloadIndex/<path:filename>")
def download_for_index(filename):
	uploads = app.config["UPLOAD_FOLDER"]
	# print(uploads)
	return send_from_directory(uploads, path=filename, as_attachment=True)#, as_attachment=True


@app.route("/upload", methods=["GET", "POST"])
def upload():
	if request.method == "POST":
		file = request.files['file']
		url = request.form.get('url')

		if file.filename != '':
			temp_file = f"{os.path.join(TEMP_UPLOAD_FOLDER)}/{file.filename}"
			# temp_file = f"data/uploads/{file.filename}"
			print(temp_file)
			file.save(temp_file)
			time.sleep(5) # wait 5 seconds after file is saved? an add torrent
			subprocess.Popen(f"transmission-remote -n 'transmission:transmission' -a {temp_file}", shell=True)
			time.sleep(60) # wait, 1 minute and then clear .torrent file
			os.remove(temp_file)
			print(f"Deleted torrent file: {temp_file}")

		elif url != '':
			# subprocess.Popen(f'echo {url}', shell=True) # debug
			subprocess.Popen(f"transmission-remote -n 'transmission:transmission' -a '{url}'", shell=True)
		# print(file.filename, url)
	# return render_template('upload.html') # debug, for seperate upload page
	return redirect('/index#upload')


@app.route("/search", methods=["GET", "POST"])
def search_torrent():
	if request.method == "POST":
		search_query = request.form.get("search_query")
		# print(search_query) # debug
		
		# with open("search_result", 'r') as f:
		# with open("testawkfull", 'r') as f:
		# 	search_result = f.read()


		# subprocess is finicky here, os.system will be used instead
		# case insensitive
		# search_result = os.system(f"transmission-remote -n transmission:transmission -l | awk 'BEGIN{{IGNORECASE = 1}}/{search_query}/;' > search_result")
		# search_result = os.system(f"transmission-remote -n transmission:transmission -l | awk 'BEGIN{{IGNORECASE = 1}}NR==1/{search_query}/{{print $1}};' > search_result")
		
		search_result = os.system(f"transmission-remote -n transmission:transmission -l | awk '/{search_query}/' > search_result")
		# search_result = os.system(f"transmission-remote -n transmission:transmission -l | awk 'NR==1/{search_query}/{{print $1}}' > search_result")
		with open("search_result", 'r') as f:
			search_result = f.read()

	return render_template("search.html", query=search_query, result=search_result)
	# return search_result


@app.route('/folder')
def folder_view():
	dirs = os.scandir()
	return render_template("folder.html", dirs=dirs, size=convert_size, timestamp=created_at, cwd=os.getcwd())


@app.route('/folderv2')
def folderv2_view():
	dirs = os.scandir()
	return render_template("folderv2.html", dirs=dirs, size=convert_size, timestamp=created_at, cwd=os.getcwd())


@app.route('/cd')
def cd():
	try:
		os.chdir(request.args.get('path'))
	except PermissionError:
		return "You do not have persmission to view this folder or file"


	# redirect to file manager depending on the route and view ?
	# not implemented
	return redirect("/folderv2")


@app.route('/md')
def md():
    # create new folder
    new_folder = request.args.get('folder')
    try:
        os.mkdir(new_folder)
    except FileExistsError:
        return "Folder or file already exists"
    # redirect to file manager
    return redirect('/folderv2')


@app.route('/rm')
def rm():
    # create new folder
    folder = request.args.get('dir')
    try:
        os.rmdir(folder) # only empty folders
    except OSError:
        return """folder is not empty, please check before deleting"""

    # redirect to file manager
    return redirect('/folderv2')


@app.route('/force-rm')
def force_rm():
    # create new folder
    folder = request.args.get('dir')
    try:
        shutil.rmtree(folder) # delete folders recursively
    except:
        return "An error occurred"
    
    # redirect to file manager
    return redirect('/folderv2')


@app.route('/view')
def view():
    # get the file content
    with open(request.args.get('file'), 'r',) as file:
        return file.read().replace('\n', '<br>')


@app.route('/rm-file')
def rm_file():
    # file = os.remove(request.args.get('file')) # deactivated intentionally 
    file = "to be deleted"
    print("Deleted ", file)
    return redirect('/folderv2')


@app.route('/view-img')
def view_img():
    img = "an image"
    print("Not implemented yet",)
    return redirect('/folderv2')




# FUNCTIONS
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


# lambda function to convert secs since unix epoch
created_at = lambda secs_since_unix_epoch: dt.strftime(
		dt.fromtimestamp(secs_since_unix_epoch), "%Y-%m-%d %H:%M:%S")




if __name__ == "__main__":
	app.run(use_reloader=True, debug=True)