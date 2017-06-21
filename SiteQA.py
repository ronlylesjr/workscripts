from bs4 import BeautifulSoup
from splinter import Browser
import datetime
import pandas as pd
import re
import requests
import time

today = datetime.datetime.now()

def findPageType(soup):
    script = soup.find('script', attrs={'language' : 'javascript'})
    pattern = re.compile("(\w+): (.*)")
    fields = dict(re.findall(pattern, script.text))
    pagetype = fields['PageType']
    return pagetype 

def dictBuilder(appurl):        #Build dictionary based on the required items on the form.
    refdict = {'1234567890' : ['Phone', 'Num', 'Amount', 'Zip'],
    'test.me@ebizautos.com' : ['Email'],
    today.strftime('%m/%d/%Y'): ['Date'],
    '01/01/1985': ['DateOfBirth'],}
    appDict = {}    
    soup = BeautifulSoup((requests.get(appurl)).text, 'html.parser')

    for field in soup.findAll('input'):
        present = False
        if field.has_attr('required'):
            for item in refdict.items():
                for ref in item[1]:
                    if ref in str(field.get('id')):
                        appDict[field.get('name')] = item[0]
                        present = True
            if not present:
                appDict[field.get('name')] = 'Test'
    return(appDict)  

def respAndError(soup):              #Takes url and determines status of page as either (Responsive/Not Responsive) and checks if link is broken or leads to 404
    try:
        if (soup.find('div', attrs={'id' : 'side-panel'})):
           respfinding = 'Responsive'
        else:
            respfinding = 'Not Responsive'
        
        if (soup.find('div', attrs={'class' : 'error404'})):
           errorfinding = '404'
        else:
            errorfinding = 'OK'         
    except:
       respfinding = 'Broken Link'
       errorfinding = 'Broken Link'
    try:
        pagetype = findPageType(soup)
    except:
        pagetype = 'N/A'
    return (respfinding, errorfinding, pagetype)   #Returns tuple

def geturls(soup, financeurl):          #Finds link for Request More Info form and Credit app.
    for link in soup.findAll('div', attrs={'class' : 'col-xs-12 col-sm-6 col-md-4'})[1].findAll('a'):       #Grab first vehicle in inventory...
        if link.has_attr('href'):
            temp = link.get('href')

            if str(temp)[:1] == '/':
                Inventoryhref = 'http:' + temp                      #Make sure the URL is in a usable format for requests
                break
            else:
                Inventoryhref = temp
                break
    srpsoup = BeautifulSoup((requests.get(Inventoryhref)).text, 'html.parser')
    srpcontact = srpsoup.find('a', attrs={'id' : 'srp-vehicle-request-more-info'})          #Go to that vehicle and grab the link for the Request More Info link
    srpform = srpcontact.get('data-source')
    soup4 = BeautifulSoup((requests.get(financeurl)).text, 'html.parser')
    financeurl = soup4.find('a', attrs={'class' : 'button button-large'})                   #Finance page was determined in build_report() and passed into this function.
    appurl = financeurl.get('href')                                                         #Find credit app link
    return(srpform, appurl)

def filloutleads(contacturl, appurl):       #Fills out lead forms specified in geturls()
    formDict = dictBuilder(contacturl)      #TODO: see if we can get addendumDict inside appDict.
    appDict = dictBuilder(appurl)
    addendumDict = {'ctlTypedSignature' : 'test', 'ctlDateSigned' : today.strftime('%m/%d/%Y')} 
    browser = Browser()
    browser.visit(contacturl)
    browser.fill_form(formDict)    
    browser.find_by_text('Send').click()
    browser.visit(appurl)
    try:
        browser.fill_form(appDict)
    except:
        pass
    page = requests.get(appurl)
    soup = BeautifulSoup(page.text, 'html.parser')    

    for menu in soup.findAll('select'):
        if menu.has_attr('required'):            
            if 'CoApplicant' in str(menu.get('id')):
                pass
            elif 'State' in str(menu.get('id')):
                browser.select(menu.get('name'), 'AL')
            elif 'Years' in str(menu.get('id')):
                browser.select(menu.get('name'), '1')
            elif 'Month' in str(menu.get('id')):
                browser.select(menu.get('name'), '1')
    browser.fill_form(addendumDict)
    browser.find_by_xpath('/html/body/section/form/div/fieldset[7]/div[1]/div[4]/div/div/div/label/span').click()
    browser.find_by_text('Submit Your Application').click()
    browser.quit()
      
def build_report(url):            
    linksummary = {}
    starttime = time.time()
    sitemap = url + 'sitemap.aspx'
    s = requests.Session()
    s.get(url)
    soup2 = BeautifulSoup((s.get(sitemap)).text, 'html.parser')
    script = soup2.find('script', attrs={'language' : 'javascript'})
    pattern = re.compile("(\w+): '(.*?)'")
    fields = dict(re.findall(pattern, script.text))
    Summarytitle = fields['DealerName'] + ' Summary.csv'
    print(fields['DealerName'])
    
    #for link in soup2.find('div', attrs={'id' : 'sitemap-content'}).findAll('a'):
    titles = [x.text for x in soup2.find('div', attrs={'class' : 'col-xs-12 col-sm-6 col-md-4'}).findAll('a') if x.has_attr('href')]
    links = [x.get('href') for x in soup2.find('div', attrs={'class' : 'col-xs-12 col-sm-6 col-md-4'}).findAll('a') if x.has_attr('href')]
    links = ['http:' + x if x[:1] == '/' else '' + x for x in links]
    comboresults = [respAndError(BeautifulSoup((s.get(x)).text, 'html.parser')) if x[0:(len(url))] == str(url) else ('Different Domain', 'Different Domain', 'N/A') for x in links]
    financeref = [comboresults.index(x) for x in comboresults if str(x[2])[:1] == '3']
    financeurl = links[financeref[0]]  
    respresults = [x[0] for x in comboresults]          #Breaks down tuple from respAndError() and puts values in lists
    errors = [x[1] for x in comboresults]        
    print(time.time()-starttime)

    linksummary['Title'] = titles                   #Build pandas DataFrame
    linksummary['Link'] = links
    linksummary['Is_Responsive'] = respresults
    linksummary['Errors'] = errors    
    df = pd.DataFrame(linksummary)
    df = df[['Title', 'Link', 'Is_Responsive', 'Errors']]
    df.to_csv('QA Summaries/' + Summarytitle)

    if df['Is_Responsive'].isin(['Not Responsive']).any() == True or df['Errors'].isin(['404']).any() == True:
        print('\aPlease check summary to see errors') 
    try:             
        theurls = geturls(soup2, financeurl)
        print('Starting browser automation...')
        filloutleads(theurls[0], theurls[1])                #Browser automation
    except: 
        print('Could not find RMI/Credit app link')

if __name__ == '__main__':
    url = input('Please paste URL: \n')
    build_report(url)
