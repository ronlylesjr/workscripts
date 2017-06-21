from bs4 import BeautifulSoup
from splinter import Browser
import re
import requests
import time
import sys

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
    results = []
    starttime = time.time()
    sitemap = url + 'sitemap.aspx'
    s = requests.Session()
    s.get(url)
    soup2 = BeautifulSoup((s.get(sitemap)).text, 'html.parser')

    links = [x.get('href') for x in soup2.find('div', attrs={'id' : 'sitemap-content'}).findAll('a') if x.has_attr('href') and '#' not in x.get('href')]
    links = ['http:' + x if x[:1] == '/' else '' + x for x in links]
    check = [scriptcheck(x) for x in links if x[0:(len(url))] == str(url)]
    ref = [check.index(x) for x in check if x == 'Present' ]
    results = set([links[x] for x in ref])

    print(time.time()-starttime)
    print(results)

if __name__ == '__main__':
    urllist = ['http://rontest1212015.beta.ebizautos.com/', 'http://www.hondaofspring.com/']
    start = time.time()
    for url in urllist:
        build_report(url)
    endtime = time.time()
    print('Complete in ' + str(endtime - start))
