from bottle import route, run, static_file, request
import os

@route("/app")
def app():
	return "Hello World"

@route('/upload_form', method='GET')
def upload_form():
    return '''
        <form action="/upload" method="post" enctype="multipart/form-data">
            Select a file: <input type="file" name="upload" />
            <input type="submit" value="Upload" />
        </form>
    '''

@route('/')
def root():
	return static_file("index.html", root="./")

@route('/upload', method='POST')
def do_upload():
    upload = request.files.get('upload')
    if upload:
        upload.save('/tmp/' + upload.filename)  # Save the file
        return 'Upload successful!'
    return 'Upload failed!'

if __name__ == '__main__':
    run(host='localhost', port=8000)
