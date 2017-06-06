from bs4 import BeautifulSoup
from splinter import Browser
import re
import requests
import time

def findPageType(soup):
    script = soup.find('script', attrs={'language' : 'javascript'})
    pattern = re.compile("(\w+): (.*)")
    fields = dict(re.findall(pattern, script.text))
    pagetype = fields['PageType']
    return pagetype 

def scriptcheck(url):
    script = '<meta name="robots" content="noindex,follow,noodp" />'
    try:
        page = requests.get(url)

        if (script) in page.text:
            scriptfinding = 'Present'
        else:
            scriptfinding = 'Not Present'
    except:
       scriptfinding = 'Broken Link'
    return(scriptfinding)    

def build_report(url):
    resultsdict = {}
    starttime = time.time()
    sitemap = url + 'sitemap.aspx'
    s = requests.Session()
    s.get(url)
    soup2 = BeautifulSoup((s.get(sitemap)).text, 'html.parser')

    for link in soup2.find('div', attrs={'id' : 'sitemap-content'}).findAll('a'):
            try: 
                if '#' not in str(link.get('href')):
                    if link.has_attr('href'):
                        if str(link.get('href'))[:1] == '/':
                            newLink = 'http:' + str(link.get('href'))  
                        else:
                            newLink = str(link.get('href'))
                            pagelinks.append(newLink)
                            pagetitles.append(link.text)
                            if not str(newLink[0:(len(url))]) == str(url):
                                resultsdict[newLink] = 'Different Domain'
                                break
                try:
                    pagesoup = BeautifulSoup((s.get(newLink)).text, 'html.parser')
                    if (str(findPageType(pagesoup))[:1] == '2'):
                        resultsdict[newLink] = scriptcheck(newLink)
                except:
                    pass
            except:
                pass 
    print(time.time()-starttime)

    for result in resultsdict.items():
        if result[1] == 'Present':
            print(result[0])

if __name__ == '__main__':
    urllist = ['http://rontest1212015.beta.ebizautos.com/', 'http://porsche-found.beta.sandbox.ebizautos.com/']
    start = time.time()
    for url in urllist:
        build_report(url)
    endtime = time.time()
    print('Complete in ' + str(endtime - start))
