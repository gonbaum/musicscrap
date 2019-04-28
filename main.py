#!/usr/bin/env python
from pprint import pprint as pp
from flask import Flask, flash, redirect, render_template, request, url_for
from music import query_api
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)
@app.route('/')
def index():
    return render_template(
        'index.html')

print('Opening browser...')


@app.route("/result" , methods=['GET', 'POST'])
def result():
    data = pd.DataFrame()
    error = None
    title = 'form no funcionando'
    if request.method == 'POST':
        title = request.form['title'] #De esta manera tomo datos del form con flask
        performer = request.form['performer']
        data = query_api(title, performer) #pido a la funcion query_api que busque los valores que le paso como args (select) y lo almaceno en resp
                #pp(resp) #pretty print la respuesta
                #if resp:
        #data = resp #si hay respuesta, almacenarla en data[]
    return render_template("result.html",  data_frame=data.to_html(classes='table100 table100-head'))  #render los resultados en el otro template
    
    #return render_template('result.html', data_frame=title)
if __name__=='__main__':
    app.run(debug=True)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
