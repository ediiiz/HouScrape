import concurrent.futures
import os
import urllib.parse

import flask
from flask import request
from imdb import IMDb
import main
import genxml
import re
from multiprocessing import pool

import time
from flask import redirect
from flask import send_from_directory
from flask import Response
from threading import Thread
from threading import Timer
import queue

app = flask.Flask(__name__, static_folder=os.path.abspath('./'))
app.config["DEBUG"] = True


q2 =[]
@app.route("/getnzb", methods=['GET'])
def init():
    while True:
        if q2.__len__() == 0 and qlogin.__len__() == 0:
            q2.append(1)
            if request.args:
                args = request.args.to_dict()
                if args["action"] == "dl" and "url" in args:
                    print(args["url"])
                    url = urllib.parse.unquote_plus(str(args["url"]))
                    try:
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            dlfile = executor.submit(main.dlfileandunpack, url).result()
                            #dlfile = main.dlfileandunpack(url)
                        if dlfile[-3:] == "nzb":
                            response = send_from_directory("./nzb/", dlfile, mimetype='application/x-nzb',
                                                               attachment_filename=dlfile, as_attachment=True)
                            response.headers["x-filename"] = dlfile
                            response.headers["Access-Control-Expose-Headers"] = 'x-filename'
                            try:
                                return response
                            finally:
                                print("")
                                if q2.__len__() != 0:
                                    q2.remove(1)
                    except:
                        if q2.__len__() != 0:
                            q2.remove(1)
                        return Response("FAILED", mimetype='text'), 404
        else:
            time.sleep(2)
            print("waiting for DL to finish")
            continue



def startsearch(imdbid, decider):
    imdb = IMDb()
    movie = imdb.get_movie(movieID=imdbid)
    check = 0
    for x in range(movie["akas"].__len__()):
        if "Germany" in movie["akas"][x]:
            movietit = str(movie["akas"][x][:-10]).replace("ä", "ae").replace("Ä", "Äe").replace("ö", "oe").replace("Ö", "oe").replace("ß", "ss")
            if decider is False:
                movietit, sep, tail = movietit.partition(' -')
                movietit, sep, tail = movietit.partition(':')
                #movietit = re.sub("[^a-zA-Z0-9 \n]", "", movietit).replace("  ", " ")
                #return str(movietit), str(movie["year"])
            movietit = re.sub("[^a-zA-Z0-9 \n]", "", movietit).replace("  ", " ")
            check = 1
            return str(movietit), str(movie["year"])
    if check == 0:
        movietit = str(movie)
        movietit = re.sub("[^a-zA-Z0-9 \n]", "", movietit).replace("  ", " ")

        return str(movietit), str(movie["year"])


def startsearchq(q, decider):
    movie = urllib.parse.unquote_plus(q)
    movieyear = movie[-4:]
    movie = movie[:(movie.__len__()-5)]
    movietit = str(movie).replace("ä", "ae").replace("Ä", "Äe").replace("ö", "oe").replace("Ö", "oe")
    if decider is False:
        movietit, sep, tail = movietit.partition(' -')
        movietit, sep, tail = movietit.partition(':')
        #movietit = re.sub("[^a-zA-Z0-9 \n]", "", movietit).replace("  ", " ")
        #return str(movietit), str(movie["year"])
    movietit = re.sub("[^a-zA-Z0-9 \n]", "", movietit).replace("  ", " ")
    return str(movietit), str(movieyear)




@app.route("/")
def opensession():
    return "logged in"


def apirequest(imdbid):
    name, year = startsearch(imdbid, True)
    urls, titles = main.searchmovie(name, year, "all")
    if titles.__len__() == 0:
        name, year = startsearch(imdbid, False)
        urls, titles = main.searchmovie(name, year, "all")
    xml = genxml.itemcreate(titles, urls)
    #q.put(xml)
    return xml


def apirequestq(q):
    name, year = startsearchq(q, True)
    urls, titles = main.searchmovie(name, year, "all")
    if titles.__len__() == 0:
        name, year = startsearchq(q, False)
        urls, titles = main.searchmovie(name, year, "all")
    xml = genxml.itemcreate(titles, urls)
    #q.put(xml)
    return xml


def start():
    session_request, output = main.login()
    return session_request


que = []
@app.route("/api")
def query():
    if request.args:
        args = request.args.to_dict()
        if "apikey" in args:
            if args["apikey"] == "a1b2c3d4":
                if args["t"] == "movie" and "imdbid" in args:
                    while True:
                        if que.__len__() == 0 and q2.__len__() == 0 and qlogin.__len__() == 0:
                            que.append(1)
                            #time.sleep(1)
                            #q = queue.Queue()
                            #Thread(target=apirequest, args=(args["imdbid"],q)).start()
                            #xml = q.get()
                            xml = apirequest(str(args["imdbid"]))
                            try:
                                return Response(xml, mimetype='text/xml')
                            finally:
                                if que.__len__() != 0:
                                    que.remove(1)
                        else:
                            time.sleep(1)
                            #print("Waiting for DL or IMDB to finish")
                            if q2.__len__() != 0:
                                continue
                if args["t"] == "search" and "q" in args:
                    while True:
                        if que.__len__() == 0 and q2.__len__() == 0 and qlogin.__len__() == 0:
                            que.append(1)
                            #time.sleep(1)
                            #q = queue.Queue()
                            #Thread(target=apirequest, args=(args["imdbid"],q)).start()
                            #xml = q.get()
                            xml = apirequestq(str(args["q"]))
                            try:
                                return Response(xml, mimetype='text/xml')
                            finally:
                                if que.__len__() != 0:
                                    que.remove(1)
                        else:
                            time.sleep(1)
                            #print("Waiting for DL or IMDB to finish")
                            if q2.__len__() != 0:
                                continue
                if args["t"] == "caps":
                    dom = open("./xmlfiles/caps.xml")
                    print(dom)
                    return Response(dom, mimetype='text/xml'), 200
                if args["t"] == "movie":
                    dom = open("./xmlfiles/2.xml")
                    print(dom)
                    return Response(dom, mimetype='text/xml'), 200
            else:
                return "Error", 404
        else:
            return "apikey missing", 404
    else:
        return "No query string received", 200


qlogin = []
@app.before_first_request
def login():
    qlogin.append(1)
    main.login()
    Timer(1200.0, login).start()
    qlogin.remove(1)


if __name__ == '__main__':
    #s, s2 = startsearch("3659388")
    #s, s2 = Thread(target=startsearch, args=[1345836]).start()
    #print(s, s2)
    #print(startsearch("4912910", True))
    #startsearch("4912910")


    app.run(host="0.0.0.0", port=int("5000"), debug=True)

    #print(startsearchq("der%20marsianer%20rettet%20mark%20watney%202015", True))


