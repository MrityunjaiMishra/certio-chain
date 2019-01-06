import datetime
import json
import pdfkit
import requests
import os
import binascii
from flask import render_template, redirect, request,send_file, url_for,Flask, flash,send_from_directory
from werkzeug.utils import secure_filename
from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []
chainLen = 0
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','pdf'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        chainLen = len(chain)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Certi-O-Chain: Decentralized '
                                 'Certification',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)
                           
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
print("STATIC "+static_file_dir)
@app.route('/certify',methods=['GET'])
def certify():
    return render_template('certificate.html',
                             title='Validation',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)
   
@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "out.pdf"
    return send_file(path, as_attachment=True)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'rb')as f:
                content = f.read()
            hextpdf = binascii.hexlify(content)
            print(hextpdf)
            get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
            response = requests.get(get_chain_address)
            if response.status_code == 200:
                content = []
                chain = json.loads(response.content)
                chainLen = len(chain)
                for block in chain["chain"]:
                    for tx in block["transactions"]:
                        
                            tx["index"] = block["index"]
                            tx["hash"] = block["previous_hash"]
                            content.append(tx)
                
            return redirect(url_for('uploaded_file',
                                    filename=filename))
            
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
@app.route('/verify', methods=['POST'])
def verify():
    pdf = request.form
    print(pdf)          
    ''' send_file(pdf,as_attachment=True)
    #converting to hex
    with open(pdf, 'rb') as f:
        content = f.read()
    hextpdf = binascii.hexlify(content)
    print(hextpdf)
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        chainLen = len(chain)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                 
                    tx["index"] = block["index"]
                    tx["hash"] = block["previous_hash"]
                    content.append(tx)
    '''
    return jsonify(request.form.to_dict())

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["courseID"]
    author = request.form["author"]
    grade = request.form["grade"]
    course_name = request.form["courseName"]

   

    now = datetime.datetime.now()
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        chainLen = len(chain['chain'])
    post_object = {
        'author': author,
        'courseName':course_name,
        'courseID': post_content,
        'grade':grade,
        
    }    
    body = """
        <html>
      <head>
        <meta name="pdfkit-page-size" content="Legal"/>
        <meta name="pdfkit-orientation" content="Landscape"/>
      </head>
        <div style="width:800px; height:600px; padding:20px; text-align:center; border: 10px solid #787878">
        <div style="width:750px; height:550px; padding:20px; text-align:center; border: 5px solid #787878">
       <span style="font-size:50px; font-weight:bold">Certificate of Completion</span>
       <br><br>
       <span style="font-size:25px"><i>This is to certify that</i></span>
       <br><br>
       <span style="font-size:30px"><b>"""+post_object['author']+"""</b></span><br/><br/>
       <span style="font-size:25px"><i>has successfully completed the course</i></span> <br/><br/>
       <span style="font-size:30px">"""+post_object['courseName']+"""</span> <br/><br/>
       <span style="font-size:20px">with grade of <b>"""+post_object['grade']+"""</b></span> <br/><br/><br/><br/>
       <span style="font-size:25px"><i>dated</i></span><br>
      <span style="font-size:30px">"""+str(datetime.datetime.now())[:19]+"""</span><br/><br/><br/><br/>
     <span style="font-size:25px"><i>certificate serial number: """+str(chainLen)+"""</i></span><br>
</div>
</div>
      </html>
    """
    pdfkit.from_string(body,"app/out.pdf")
    #converting to hex
    with open("app/out.pdf", 'rb') as f:
        content = f.read()
    hextpdf = binascii.hexlify(content)
    post_object['hexedpdf']=str(hextpdf)
    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
