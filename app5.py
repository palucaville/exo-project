''' webapp to upload a RAW image to a folder and convert it to JPG,
The index.html page shows the upload form and Thumbnail of the files processed.

'''
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
#from PIL import Image
from datetime import datetime
import rawpy
import imageio
import os
import hashlib



#datestamp = datetime.now().date()
#posix_time = datetime.now().timestamp()


BUF_SIZE = 65536  #  64kb chunks buffer for hashing!



app = Flask(__name__)
#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.crw','.cr2','.nef'] # case NON sensitive
app.config['UPLOAD_PATH'] = 'uploads'
app.config['TESTING'] = True
app.config['DEBUG'] = True

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    jpg_files = []

    for afile in files:
        if afile.endswith('.jpg'):
            jpg_files.append(afile)
            #sha_text, md5_text = hash_file(os.path.join(app.config['UPLOAD_PATH'], afile))
            #print(sha_text, md5_text)
    #return render_template('index.html', files=jpg_files , sha_t=sha_text , md5_t=md5_text)
    return render_template('index.html', files=jpg_files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    sha_text = ""
    md5_text = ""
    ## some file check
    if filename != '':
        file_ext = (os.path.splitext(filename)[1]).lower()
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        ## do the hashing
        sha_text, md5_text = hash_file(os.path.join(app.config['UPLOAD_PATH'], filename))
        print(sha_text, md5_text)
        ## do the conversion and delete RAW
        convertRaw(os.path.join(app.config['UPLOAD_PATH'], filename), filename)
        # delete uploaded RAW iage
        os.remove(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))

def convertRaw(raw_in, fname):
    datestamp = datetime.now().isoformat()
    raw = rawpy.imread(raw_in)
    rgb = raw.postprocess()
    imageio.imsave(os.path.join(app.config['UPLOAD_PATH'], f'{fname}_{datestamp}.jpg'), rgb)
    

def hash_file(raw_in):
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    with open(raw_in, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
            md5.update(data)
    md5_text = ("MD5: {0}".format(md5.hexdigest()))
    sha_text = ("SHA1: {0}".format(sha1.hexdigest()))
    return sha_text, md5_text


@app.route('/uploads/<filename>') ## serves a page with the new converted file
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == "__main__":
    app.run(debug = True)
