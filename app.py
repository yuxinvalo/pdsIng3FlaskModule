import os
from flask import Flask, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask import render_template
import utils
import datetime
from flask import request

import predict
import pandas as pd
import random


app = Flask(__name__)
app.debug = True
UPLOAD_FOLDER = 'upload/'
ALLOWED_EXTENSIONS = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'toto'

@app.route('/', methods=['GET', 'POST'])
def index():
    availableDate = utils.getAvailableDate('resources/yearHistoryTemplate.csv')
    if request.method == "POST":
        if request.form['Submit'] == 'Submit':
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]
            print(startDate + " " + endDate)
            if(utils.validateDate([startDate, endDate])):
                targetBooking = utils.loadHistoryByDate(startDate, endDate)
                targetBookingLimit = targetBooking.head(20)
                files =  utils.getFileInHadoop()
                session['startDate'] =  startDate
                session['endDate'] = endDate
                return render_template("bookings.html", tables=[targetBookingLimit.to_html(classes='data')], \
                titles=targetBooking.columns.values, msg="Amount of booking is" + str(targetBooking.shape[0]) + \
                " between " + startDate + " and " + endDate + ".", options=files)
            else:
                return render_template("error.html", options=[startDate, endDate])
    return render_template('hello.html', options=availableDate)

@app.route('/upload', methods=['GET', 'POST'])
def getUploadFile():
    format = "%Y-%m-%dT%H:%M:%S"
    now = datetime.datetime.utcnow().strftime(format)
    if request.method == 'POST':
        f = request.files['file']
        filename = now + '_' + f.filename
        filename = secure_filename(filename)
        if utils.checkUploadFile(filename):
            # f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            client_hdfs = utils.getClientHadoop()
            df = pd.read_csv(f)
            utils.saveToHadoop(df, filename, client_hdfs)
        else:
            return 'This is not a csv file.'
    else:
        return 'no file chosen'
    return 'file uploaded successfully'

@app.route('/load', methods=['GEI', 'POST'])
def loadCurrentExternFile():
    if request.method == "POST":
        if request.form['Submit'] == 'SubmitFile':
            selectedFile = request.form["extFile"]
            session['selectedFile'] = selectedFile
            df = pd.read_csv(selectedFile)
            return render_template('bookings.html', options=df.columns.values, selected=True)
        elif request.form['Submit'] == 'SubmitCol':
            mapped = request.form['mapCol']
            integCol1 = request.form['integCol1']
            integCol2 = request.form['integCol2']
            integCol3 = request.form['integCol3']
            integrateCols = [integCol1, integCol2, integCol3]
            df = utils.integrateData(mapped, integrateCols, session.get('startDate'), \
            session.get('endDate'), session.get('selectedFile'))
            dfH = df.head(10)
            return render_template("integration.html", tables=[dfH.to_html(classes='data')], \
            titles=dfH.columns.values)
    return "none"

if __name__ == '__main__':
    app.run()
