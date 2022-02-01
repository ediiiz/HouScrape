import main
import re
import urllib.parse

def itemcreate(titles,urls):
    xml = ""
    count = 0
    xml += xmlhead
    for x in range(titles.__len__()):
        title = titles[x]
        title = urllib.parse.quote_plus(title)
        url = urls[x]
        url = urllib.parse.quote_plus(url)
        url = str("http://athomefb.spdns.de:61001/getnzb?action=dl&amp;url=" + str(url))
        #urldebug = main.thank_urls[x].replace("&", "&amp;")
        quality = "test"
        imdb = "test"
        x = str(x)
        xmlitem = '''
  <item>
   <title>''' + title + '''</title>
   <guid isPermaLink="true">'''+url+'''</guid>
   <link>'''+url+'''</link>
   <comments>test</comments>
   <pubDate>2'''+x+''' Oct 2019</pubDate>
   <category>2040</category>
   <description>''' + title + '''</description>
   <enclosure url="'''+url+'''" length="1''' + x + '''813232292" type="application/x-nzb"/>
   <newznab:attr name="category" value="''' + x + '''"/>
   <newznab:attr name="size" value=""/>
   <newznab:attr name="coverurl" value=""/>
   <newznab:attr name="files" value=""/>
   <newznab:attr name="poster" value="'''+x+'''"/>
   <newznab:attr name="imdb" value=""/>
   <newznab:attr name="grabs" value=""/>
   <newznab:attr name="comments" value=""/>
   <newznab:attr name="password" value="'''+x+'''"/>
   <newznab:attr name="usenetdate" value=""/>
   <newznab:attr name="group" value="alt.binaries.ath"/>
  </item>'''
        xml += xmlitem
        count += 1
    xml += xmltail
    return xml


xmlhead ='''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:newznab="http://www.newznab.com/DTD/2010/feeds/attributes/" encoding="utf-8">
 <channel>
  <atom:link href="https://scenenzb.com/api" rel="self" type="application/rss+xml"/>
  <title>SceneNZB</title>
  <description>SceneNZB API Details</description>
  <link>https://scenenzb.com/</link>
  <language>en-gb</language>
  <webMaster>scenenzbindexer@protonmail.ch SceneNZB</webMaster>
  <category>usenet,nzbs,cms,community</category>
  <generator>nZEDb</generator>
  <ttl>10</ttl>
  <docs>https://scenenzb.com/apihelp/</docs>
  <image url="https://scenenzb.com/themes/shared/img/logo.png" title="SceneNZB" link="https://scenenzb.com/" description="Visit SceneNZB - "/>
  <newznab:response offset="0" total="'''+str(2)+'''"/>'''



xmltail = '''
 </channel>
</rss>'''

if __name__ == "__main__":
    print(itemcreate(["test", "test"]))