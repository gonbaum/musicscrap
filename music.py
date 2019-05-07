import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import DataFrame
import numpy as np
from flask import Flask,render_template, request

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")

pd.set_option('display.max_columns', None)
pd.set_option("display.max_colwidth", 10000)

songtitle = ""


def query_api(songtitle, perfname):
  
    #BMI
    att='Y'

    def BMI(input_name):

    #QUITAR COMENTARIOS PARA USAR ONLINE CUANDO TERMINE SCRAP
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("http://repertoire.bmi.com/StartPage.aspx")
        searchBar = driver.find_element_by_xpath("//input[@id='searchControl_txtSearchFor']")
        searchBar.send_keys(input_name)
        searchButton = driver.find_element_by_xpath("//*[@id='searchControl_btnSubmit']").click()
        searchButton = driver.find_element_by_xpath("//*[@id='btnSubmit']").click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        titles = []
        writers = []
        source = []

        tableresultstitles = soup.find_all('tr', class_='work-title-header')
        tableresultswriters = soup.find_all('div', class_='table-responsive')

        #BUSQUEDA DE TITULOS
        for tr in tableresultstitles:
            worktitles = tr.find_all('td', class_='work_title')[0].get_text()
            titles.append(worktitles)
            
        #BUSQUEDA DE WRITERS

        for i in tableresultswriters:
            writersnames = i.find_all('a', href =re.compile('Catalog.aspx'))
            
            local_array = []
            for a in writersnames:   
                local_array.append(a.get_text())
            writers.append(local_array)
            
        print(titles)
        print(writers)

        
        return titles, writers
    
    returnbmi =(BMI(songtitle))


    if perfname == "":
        
        if (att == "y") or (att == "Y"):
            ascap = requests.get('https://www.ascap.com/api/wservice/MobileWeb/service/ace/api/v2.0/works/details?limit=100&page=1&universe=IncludeATT&workTitle=' + songtitle)
        elif (att == "N") or (att == "n"):
            ascap = requests.get('https://www.ascap.com/api/wservice/MobileWeb/service/ace/api/v2.0/works/details?limit=100&page=1&universe=OTTOnly&workTitle=' + songtitle)
        else:
            print("Must enter Y or N, search will be performed including alternate titles...\n")
            ascap = requests.get('https://www.ascap.com/api/wservice/MobileWeb/service/ace/api/v2.0/works/details?limit=100&page=1&universe=IncludeATT&workTitle=' + songtitle)
        print('Searching for title(' + songtitle + '), -no performer name-...')
        
    else:
        if (att == "y") or (att == "Y"):
            ascap = requests.get('https://www.ascap.com/api/wservice/MobileWeb/service/ace/api/v2.0/search/title/' + songtitle + '?limit=100&page=1&universe=IncludeATT&searchType2=perfName&searchValue2=' + perfname)
        elif (att == "N") or (att == "n"):
            ascap = requests.get('https://www.ascap.com/api/wservice/MobileWeb/service/ace/api/v2.0/search/title/' + songtitle + '?limit=100&page=1&universe=OTTOnly&searchType2=perfName&searchValue2=' + perfname)
        else:
            print("Must enter Y or N, search will be performed including alternate titles...")
            ascap = requests.get('https://www.ascap.com/api/wservice/MobileWeb/service/ace/api/v2.0/search/title/' + songtitle + '?limit=100&page=1&universe=IncludeATT&searchType2=perfName&searchValue2=' + perfname)

        print('Searching for title(' + songtitle + '), performer name(' + perfname + ')...')


    writerascap = []
    performerascap = []
    titleascap = []

    json_data = ascap.json()

    if json_data['result'] is None:
        print(json_data['error']['description'])
    elif json_data['result'] == []:
        print('No matches were found for this search')
        if json_data['meta']['attCount']:
            attCount = str(json_data['meta']['attCount'])
            print('There are ' + attCount + ' alternative titles found.')
    else:          
        a = 0
        print('Results found: \n')
        for results in json_data['result']:
            a = a + 1
            print (str(a) + ':')                     
            print ('Work Title: ' + results["workTitle"])
            titleascap.append(results["workTitle"])

            local_array = []
            for interestedParties in results["interestedParties"]:
                if interestedParties["roleCde"] == "W":
                    print ('Writer: ' + interestedParties["fullName"])
                    local_array.append(interestedParties["fullName"])
                elif interestedParties["roleCde"] == "P":
                    print ('Other interested parties: ' + interestedParties["fullName"])
            writerascap.append(local_array)
                    
            if results["performers"] is None:
                print ('Performers: -None-')
            else:
                local_array = []
                for performers in results["performers"]:
                    print ('Performers: ' + performers['fullName'])
                    local_array.append(interestedParties["fullName"])
            performerascap.append(local_array)
            print('\n')
                              
    
    
    returnascap = [titleascap, writerascap, performerascap]
    
    print(len(returnbmi[0]))
    print(returnbmi[0])
    print(len(returnbmi[1]))
    print(returnbmi[1])
    print(len(returnascap[0]))
    print(returnascap[0])
    print(len(returnascap[1]))
    print(returnascap[1])

    #BUILDING DATAFRAME

    cols = ['Source', 'Titles', 'Writers']
    cols2 = ['Source', 'Titles', 'Writers', 'Performers' ]

    dataframebmi = pd.DataFrame({ 'Source': 'BMI', 'Titles': returnbmi[0],
                                'Writers': returnbmi[1]
                                })[cols]
    print(dataframebmi)

    
    dataframeascap = pd.DataFrame({'Source': 'ASCAP', 'Titles': returnascap[0],
                                    'Writers': returnascap[1], 'Performers': returnascap[2]
                                    })[cols2]
        
    print(dataframeascap)

    test = pd.concat([dataframeascap, dataframebmi], axis=0, ignore_index=True, sort = False)

    return test
