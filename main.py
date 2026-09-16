from bottle import route, run, static_file, request
import os

@route("/app")
def app():
	return "Hello World"

@route("/upload", method="POST")
def upload():
	category = request.forms.get('category')
	upload = request.files.get('upload')
	name, ext = os.path.splitext(upload.filename)
	if ext not in (".png", ".jpg", ".jpeg", ".mp4"):
		return "File uploaded not allowed!"

	save_path = "/tmp/{category}".format(category=category)
	if not os.path.exists(save_path):
		os.makedirs(save_path)

	file_path = "{path}/{file}".format(path=save_path, file=upload.filename)
	upload.save(file_path)
	return "File successfully saved to '{0}'.".format(save_path)

if __name__ == "__main__":
	run(host="0.0.0.0", port=8080, debug=True, reload=True)