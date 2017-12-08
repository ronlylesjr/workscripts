from bs4 import BeautifulSoup
import requests
import time
import concurrent.futures

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
    return (url, scriptfinding)

def build_report(url):
    sitemap = url + 'sitemap.aspx'
    s = requests.Session()
    s.get(url)
    soup2 = BeautifulSoup((s.get(sitemap)).text, 'html.parser')

    links = (x.get('href') for x in soup2.find('div', 
            attrs={'id' : 'sitemap-content'}).findAll('a') if x.has_attr('href') 
            and '#' not in x.get('href'))
    
    links = ('http:' + x if x[:1] == '/' else x for x in links)
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        result = executor.map(scriptcheck, links)

    print(set(x[0] for x in result if x[1] == 'Present'))

if __name__ == '__main__':
    urllist = ['http://rontest1212015.beta.ebizautos.com/']
    start = time.time()
    for url in urllist:
        build_report(url)
    endtime = time.time()
    print('Complete in ' + str(endtime - start))
