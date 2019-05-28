#!/usr/bin/env python
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from music import query_api
import pandas as pd
import time

app = Flask(__name__)
Bootstrap(app)

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
        title = request.form['title'] 
        performer = request.form['performer']
        data = query_api(title, performer) 

    return render_template("result.html",  data_frame=data.to_html(classes='table table-responsive table-striped', bold_rows=True).replace('border="1"','border="0"'))  #render los resultados en el otro template
    

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
