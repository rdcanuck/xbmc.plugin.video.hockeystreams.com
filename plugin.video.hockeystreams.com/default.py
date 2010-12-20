import urllib,urllib2,re,xbmcplugin,xbmcgui,mechanize,cookielib,string
from xml.dom.minidom import parseString
#
# HockeyStreams.com Scraper v2.0
# original author: James Atkinson <james@theatkinsons.ca>
# updated on December 5, 2010
# by: rdcanuck <rdcanuck@gmail.com>
#
# Changlog:
# v1.0
# - Initial Creation
# v2.0
# added Dharma addon support. Now runs in XBMC v10 (Dharma)
# as part of new addon repository design
# added addon.xml file + logo.png 
# v2.01
# url changed from www. to www6.
              
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
def getDateFromUser():
        loop = True
        while(loop):
                kb = xbmc.Keyboard('', '', True)
                kb.setHeading('Enter Date to Search (MM-DD-YYYY)')
                kb.setHiddenInput(False)
                kb.doModal()
                if (kb.isConfirmed()):
                        date = kb.getText()
                        loop = False
                else:
                        return(False)
        return(date)

def addIpException(browser):
        # Add an IP exception
        browser.open('http://www6.hockeystreams.com/include/exception.inc.php')
        browser.select_form(nr=0)
        browser.submit()


def CATEGORIES():
        addDir('Live Games', 'http://www6.hockeystreams.com/rss/streams.php', 1, '')
        addDir('Archives', 'http://www6.hockeystreams.com/hockey_archives', 2, '')
        addDir('Add IP Exception', '', 9, '')
                       
def ARCHIVES(browser, url):
        user_date = getDateFromUser()
        if (user_date):
                response = browser.open(url + "/" + user_date)
                page_content = response.read()
                match = re.compile('<a href="(.+?)" class="buttonrev" style="float: left;">').findall(page_content)
                for url in match:
                        parts = string.split(url, '/')
                        addDir(re.sub('_', ' ', parts[3]), 'http://www6.hockeystreams.com' + url, 3, '')

def LIVE_STREAMS(browser, url):
        response = browser.open(url)
        page_content = response.read()
        dom = parseString(page_content)
        items = dom.getElementsByTagName('item')
        for item in items:
                title = ""
                description = ""
                for parts in item.childNodes:
                        if parts.nodeName == "title":
                                for textNode in parts.childNodes:
                                        if textNode.nodeType == textNode.TEXT_NODE:
                                                title = textNode.nodeValue
                        if parts.nodeName == "description":
                                for textNode in parts.childNodes:
                                        if textNode.nodeType == textNode.TEXT_NODE:
                                                description = textNode.nodeValue
                
                match = re.compile('(.*?)<a href="(.*?)">.*?').findall(description)
                title = title + " " + match[0][0].strip() + " EST"
                
                last_slash = match[0][1].rfind('/')
                stream_url = match[0][1][0:last_slash]
                addDir(title, stream_url + '/', 4, '')

def CHOOSE_ARCHIVE_STREAM(browser, url):
        response = browser.open(url);
        page_content = response.read()
        match = re.compile('<a class="tvicon" href="(.+?)" style=".+?">').findall(page_content)
        for url in match:
                parts = string.split(url, '/')
                
                # We have to fetch the stream pages in order to get the stream urls
                stream_response = browser.open('http://www6.hockeystreams.com' + url)
                stream_page_content = stream_response.read()
                stream_match = re.compile('<div style="border-bottom: 1px dashed #cecece; padding: 5px;"><input type="text" id="direct_link" readonly value="(.+?)" style="width: 285px; padding: 5px; height: 20px; line-height: 20px; border: 1px solid #cecece;" />').findall(stream_page_content)
                for stream_url in stream_match:
                        addLink(string.capitalize(re.sub('_', ' ', parts[5])), stream_url, '')

def CHOOSE_LIVE_STREAM(browser, url):
        response = browser.open(url);
        page_content = response.read()
        match = re.compile('<a class="tvicon" href="(.*?)".*?').findall(page_content)
        for url in match:
                parts = string.split(url, '/')

                # We have to fetch the stream pages in order to get the stream urls
                stream_response = browser.open('http://www6.hockeystreams.com' + url)
                stream_page_content = stream_response.read()
                stream_match = re.compile('readonly value="(.+?)"').findall(stream_page_content)
                for stream_url in stream_match:
                        addLink(string.capitalize(re.sub('_', ' ', parts[4])), stream_url, '')

              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

# Setup our browser
jar = cookielib.CookieJar()
browser = mechanize.Browser()
browser.set_cookiejar(jar)

# Browser options
browser.set_handle_equiv(True)
browser.set_handle_redirect(True)
browser.set_handle_referer(True)
browser.set_handle_robots(False)

# We pretend we're a normal browser, just in case
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Login
resp = browser.open('http://www6.hockeystreams.com')
browser.select_form(nr=0)
browser['username'] = xbmcplugin.getSetting(int (sys.argv[1]), 'username')
browser['password'] = xbmcplugin.getSetting(int (sys.argv[1]), 'password')
browser.submit()

if mode==None or url==None or len(url)<1:
        CATEGORIES()
      
elif mode==1:
        LIVE_STREAMS(browser,url)
        
elif mode==2:
        ARCHIVES(browser,url)

elif mode==3:
        CHOOSE_ARCHIVE_STREAM(browser, url)

elif mode==4:
        CHOOSE_LIVE_STREAM(browser, url)

elif mode==9:
        addIpException(browser)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
