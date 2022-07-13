from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.fciykbx.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route("/")
def movie_get():
    movie_list = list(db.mumu_movie.find({}, {'_id': False}))
    return render_template("index.html", moviej=movie_list)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)