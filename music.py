import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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

def clean_names(names_list):
    cleaned_names = []
    for name in range(len(names_list)):
        my_lst_str = ', '.join(map(str, names_list[name]))
        cleaned_names.append(my_lst_str)
    return cleaned_names

def query_api(songtitle, perfname):
  
    #BMI
    att='Y'

    def BMI(input_name):

        driver = webdriver.Chrome(chrome_options=chrome_options)
        delay = 3
        driver.get("http://repertoire.bmi.com/StartPage.aspx")
        searchBar = driver.find_element_by_xpath("//input[@id='searchControl_txtSearchFor']")
        searchBar.send_keys(input_name)
        driver.find_element_by_xpath("//*[@id='searchControl_incArtists']").click()
        driver.find_element_by_xpath("//*[@id='searchControl_btnSubmit']").click()
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'btnSubmit')))
        driver.find_element_by_xpath("//*[@id='btnSubmit']").click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        titles = []
        writers = []
        artists = []
        result = []


        tableresultstitles = soup.find_all('tr', class_='work-title-header')
        tableresultswriters = soup.find_all('div', class_='table-responsive')

        #BUSQUEDA DE TITULOS
        for tr in tableresultstitles:
            worktitles = tr.find_all('td', class_='work_title')[0].get_text().title()
            titles.append(worktitles)
            
        #BUSQUEDA DE WRITERS
        for i in tableresultswriters:
            writersnames = i.find_all('a', href =re.compile('writerid'))
            local_array = []
            for a in writersnames:   
                local_array.append(a.get_text().title())
            writers.append(local_array)

        #BUSQUEDA DE ARTISTS
        for i in tableresultswriters:
            artistsnames = i.find_all('a', href =re.compile('artistid'))
            local_array2 = []
            for a in artistsnames:   
                local_array2.append(a.get_text().title())
            artists.append(local_array2)    

        print(titles)
        print(writers)
        print(artists)

        result.append(titles)
        result.append(writers)
        result.append(artists)
        result[1] = clean_names(result[1])
        result[2] = clean_names(result[2])

        return result
    
    returnbmi = BMI(songtitle)
    

    #ASCAP API search

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

            local_array_w = []
            for interestedParties in results["interestedParties"]:
                if interestedParties["roleCde"] == "W":
                    print ('Writer: ' + interestedParties["fullName"])
                    local_array_w.append(interestedParties["fullName"])
                elif interestedParties["roleCde"] == "P":
                    print ('Other interested parties: ' + interestedParties["fullName"])
            writerascap.append(local_array_w)
            
            local_array_p = []        
            if results["performers"] is None:
                print ('Performers: -None-')
            else:
                for performers in results["performers"]:
                    print ('Performers: ' + performers['fullName'])
                    local_array_p.append(performers["fullName"])
            performerascap.append(local_array_p)
            print('\n')

    for names in range(len(titleascap)):
        titleascap[names] = titleascap[names].title()

    writerascap = clean_names(writerascap)
    performerascap = clean_names(performerascap)
    returnascap = [titleascap, writerascap, performerascap]
    
    print(len(returnbmi[0]))
    print(returnbmi[0])
    print(len(returnbmi[1]))
    print(returnbmi[1])
    print(len(returnbmi[2]))
    print(returnbmi[2])
    print(len(returnascap[0]))
    print(returnascap[0])
    print(len(returnascap[1]))
    print(returnascap[1])

    #BUILDING DATAFRAME

    cols = ['Source', 'Titles', 'Writers', 'Performers']
    cols2 = ['Source', 'Titles', 'Writers', 'Performers' ]

    dataframe_bmi = pd.DataFrame({ 'Source': 'BMI', 'Titles': returnbmi[0],
                                'Writers': returnbmi[1], 'Performers': returnbmi[2]
                                })[cols]
    print(dataframe_bmi)

    dataframe_ascap = pd.DataFrame({'Source': 'ASCAP', 'Titles': returnascap[0],
                                    'Writers': returnascap[1], 'Performers': returnascap[2]
                                    })[cols2]

    dataframe_ascap['Writers'] = dataframe_ascap['Writers'].astype(str).str.title()
    dataframe_ascap['Performers'] = dataframe_ascap['Performers'].astype(str).str.title()

    print(dataframe_ascap)

    dataframe_complete = pd.concat([dataframe_ascap, dataframe_bmi], axis=0, ignore_index=True, sort = False)
    dataframe_complete = dataframe_complete.fillna('-')

    return dataframe_complete
