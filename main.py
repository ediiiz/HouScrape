'''
Scraper für House of Usenet um NZB dateien zu finden und entpacken und password ergänzen.
ToDo:
1. Login beim myBB mit php form data !Done
2. Search form data mit variablen !Done
4. open thank url !done
5. download nzb !done
6. if archive then unpack !done
7. write password into nzb !done
8. distribute !done

Bugs:
Manchmal gibt die search kein Ergebniss wenn man zu schnell nacheinander sucht
'''
import urllib.parse
import cloudscraper
from bs4 import BeautifulSoup
import re
import patoolib
import os
import xml.etree.ElementTree as ET

baseurl = "https://house-of-usenet.com"
search_url = "https://house-of-usenet.com/search.php"

logindata = {
"action": "do_login",
"url": "/index.php",
"my_post_key": "xx",
"username": "",
"password": "",
"remember": "yes",
}


searchdata = {
"action": "do_search",
"keywords": "",
"postthread": "1",
"author": "",
"matchusername": "1",
"findthreadst": "1",
"numreplies": "",
"postdate": "0",
"pddir": "1",
"threadprefix[]": "any",
"forums[]": ["63", "76"],
"submit": "Suche",
}

session_request = cloudscraper.CloudScraper(browser={'browser': 'chrome'}, debug=False)

def quality(i):
    switcher = {
        "720": '28',
        "1080": '63',
        "3D": '40',
        "2160": '76'
    }
    return switcher.get(i, "xxx")

loginint = []
def login():
    print(login.__name__)
    result = session_request.get(baseurl + "/index.php").text
    my_post_key = re.search('var my_post_key\s+=\s+"([^"]+)', result).group(1)
    #print(my_post_key)
    if my_post_key:
        logindata["my_post_key"] = my_post_key

    result = session_request.post(baseurl + "/member.php", data=logindata, headers=dict(referrer=baseurl + "/index.php"))
    loginint.append(1)
    return session_request, print("logged in")


def searchmovie(name, year, quality_string):
    print(searchmovie.__name__, name, year)
    #login()
    quality_string_output = quality(quality_string)
    if quality_string_output is not "xxx":
        searchdata["keywords"] = name + " " + year
        searchdata["forums[]"] = quality_string_output
        search = session_request.post(search_url, searchdata,
                                      headers=dict(referrer=search_url))
        soup = BeautifulSoup(search.content, "html.parser")
        return getthreadIDs(soup)
    else:
        keyword = name + " " + year
        keyword = urllib.parse.quote_plus(keyword)
        print(keyword)
        searchdatastring = "action=do_search&keywords=" + keyword \
                           + "&postthread=1&author=&matchusername=1&findthreadst=1&numreplies=&postdate=0&pddir=1&threadprefix%5B%5D=any&forums%5B%5D=26&forums%5B%5D=30&forums%5B%5D=93&forums%5B%5D=27&forums%5B%5D=1865&forums%5B%5D=28&forums%5B%5D=63&forums%5B%5D=76&submit=Suche"
        search = session_request.post(search_url, searchdatastring,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded'})
        soup = BeautifulSoup(search.content, "html.parser")
        return getthreadIDs(soup)


#test = open("./test.html", encoding="utf8")
#contents = test.read()
#soup = BeautifulSoup(contents, "lxml")

def gettitle(soup):
    titles = []
    anchors = soup.select("table.tborder > tr.inline_row > td > span.smalltext > a:nth-of-type(1)")
    for x in anchors:
        title = str(x.text).strip()
        title = title.replace(" ", ".")
        #print(title)
        #mystr = str(anchors[x]).strip()
        #title = mystr[mystr.find(">") + 1: mystr.find("[")]
        #title = re.search(" (.*)", str(anchors[x]).strip())
        #print(str(anchors[x]).replace("  ", "").strip())
        if title not in titles:
            titles.append(title)
    return titles

def getthreadIDs(soup):
    print(getthreadIDs.__name__)
    thank_urls = []
    for a in soup.find_all('a', href=re.compile("pid=")):
        tid = re.search("tid=(.*?)&", a['href']).group(1)
        pid = re.search("pid=(.*?)&", a['href']).group(1)
        thank_urls.append(getthxurl(tid, pid))
    return thank_urls, gettitle(soup)

def getthxurl(tid, pid):
    return "https://house-of-usenet.com/showthread.php?action=thank&tid=%s&pid=%s" % (tid, pid)

def scrape(url):
    return session_request.get(url).content


def getdllink(thank_url):
    print(getdllink.__name__)
    try:
        thankedpage = scrape(thank_url)
        #test = open("./thanked.html", encoding="utf8")
        #thankedpage = test.read()
        soup = BeautifulSoup(thankedpage, "lxml")
        for a in soup.find_all('a', href=re.compile("aid=")):
            url = re.search("aid=(.*)", a['href'])
            url = url.group(1)
            return "https://house-of-usenet.com/attachment.php?aid=%s" % url, a.text
    except RuntimeError:
        print("No AID")

def dlfileandunpack(thank_url):
    while True:
        if loginint.__len__() != 0:
            #print(thank_url)
            dlurl, filename = getdllink(thank_url)
            filename = filename.replace(" ", ".")
            try:
                r = session_request.get(dlurl)
                with open('./temp/' + filename, 'wb') as f:
                    f.write(r.content)
                if filename[-3:] == "rar":
                    print("unpacking")
                    patoolib.extract_archive('./temp/' + filename, outdir="./temp", interactive=False)
                    os.remove("./temp/" + filename)
                    dirs = os.listdir("./temp")
                    filenameunpacked = dirs[0]
                    filenameunpacked = filenameunpacked.replace(".nzb", "").replace(".rar", ".nzb")
                    filenamefin = passtonzb(filenameunpacked + ".nzb")
                    print("ReturnDL: " + filenamefin)
                    return filenamefin
                else:
                    #print("Mod NZB")
                    filename = filename.replace(".nzb", "").replace(".rar", ".nzb")
                    filenamefin = passtonzb(filename + ".nzb")
                    print("ReturnDL: " +filenamefin)
                    return filenamefin
            except RuntimeError:
                print("No Attachment to DL")
        else:
            continue

def cleanup(what):
    try:
        if what == "temp":
            dir = os.listdir("./temp")
            if dir.__len__() != 0:
                os.remove("./temp/" + dir[0])
        if what == "nzb":
            dir2 = os.listdir("./nzb")
            if dir2.__len__() !=0:
                os.remove("./nzb/" + dir2[0])
    except:
        print("no removal")


def passtonzb(filename):
    try:
        password = re.search("{{(.*)}}", filename).group(1)
        tree = ET.parse("./temp/" + filename)
        root = tree.getroot()
        head = ET.SubElement(root, "head")
        meta = ET.SubElement(head, "meta", type="password").text = password
        tree.write("./nzb/" + filename)
        os.remove("./temp/" + filename)
        return filename
    except:
        cleanup("temp")
        print("failed to mod")



if __name__ == "__main__":
    #print(getdllink(""))
    #test = open("./test.html", encoding="utf8")
    #contents = test.read()
    #soup = BeautifulSoup(contents, "lxml")

    #print(getthreadIDs(soup))

    #login()
    #print(searchmovie("The Dark Knight Rises", "2012", "all"))
    #displayall()
    print("Next")
    #searchmovie("interstellar", "2014", "all")
    #displayall()


    #print(getdllink(""))

    #dlfileandunpack("")

    #search("joker", "2019")
    #result = session_request.get(baseurl+logindata["url"])
    #print(result.content)

