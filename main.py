# Скрипт для опроса и получения данных ИБП фирмы Eaton, Entel по HTTP.

import requests, json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

print ("""
 _   _ ____  ____  _                _              
| | | |  _ \/ ___|| |__   __ _ _ __| | __          
| | | | |_) \___ \| '_ \ / _` | '__| |/ /          
| |_| |  __/ ___) | | | | (_| | |  |   <           
 \___/|_|   |____/|_| |_|\__,_|_|  |_|\_\          

work in progress

Started UPShark script ver. 1.04              
""")

class GetUPS():
    # read UPS list from Json when object is called
    def __init__(self):
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        with open('ups_list.json', 'r+', encoding='utf-8') as file:
                self.ups_list = json.load(file)
        s = Service('firefoxdrivers/geckodriver')
        o = Options(); o.add_argument('--headless')
        self.driver = webdriver.Firefox(service=s, options=o)
        
        self.table_eaton = ['UPS Eaton report','[____________NAME____________][STATUS]']
        self.table_entel = ['UPS Entel report','[____________NAME____________][STATUS]']
        self.table_lpm =   ['UPS LPM report', '[_____________NAME___________][STATUS]']
        

    #Eaton functions
    def getEatonPage(self):
        for i in (self.ups_list['eaton']):
            #CombineURl URL 
            combUrl = 'http://'+self.ups_list['eaton'][i]+'/ups_propAlarms.htm'
            try:
                req = requests.get(combUrl)
                print(i, 'UPS EATON')
                print('!INFO Successful connected to UPS at destination', self.ups_list['eaton'][i])
                req.encoding = "utf-8"
                page = req.text
                self.checkError_Eaton(page, i)
            except:
                print(i, '!ERROR Connection timed out\n')
                self.table_eaton.append('Conn. timed out')

    def checkError_Eaton(self, page: str, ups_name: str) -> int:
        soup = BeautifulSoup(page, 'lxml')
        errors = []
        errors = soup.find_all(class_='listline1')
        try:        
            if len(errors) > 0:
                print(f'Detected {len(errors)} alarms!')
                print('!UPS Alarm: CHECK UPS')
                dataString = f'{ups_name}'
                self.table_eaton.append(dataString.ljust(30)+f'ALARM! ({len(errors)})!')
                return len(errors)
            else:
                print('Status OK\n')
                dataString = f'{ups_name}'
                self.table_eaton.append(dataString.ljust(30)+'OK')
                return len(errors)
        except Exception as ex:
            print('!ERROR Something went wrong! Unexpected result\n',ex)

    # Entel functions
    def getEntelPage(self):
        for i in self.ups_list['entel']:
            combUrl = 'http://'+self.ups_list['entel'][i]['ipaddres']+'/status.htm'
            
            try:
                num = 1
                status = True
                while status:
                    req = requests.get(combUrl, 
                                    auth=(
                                    self.ups_list['entel'][i]['login'],
                                    self.ups_list['entel'][i]['password']
                                    ), headers=self.headers)
                    print(i, '!INFO connected. Status code: ',req.status_code)
                    if req.status_code == 200:
                        print('!INFO Authorized. Parse data.')
                        status = False
                        page = req.text
                        print('UPS ENTEL')
                        print('!INFO Successful connected to UPS at destination', self.ups_list['entel'][i]['ipaddres'])
                        self.checkError_Entel(page, i)
                        print('\n') 
                    else:
                        print('!ERROR authorization fail.')
                        print('!INFO Retry connect. Tries:', num)
                        num+=1
                               
            except:
                print('!ERROR Connection timed out')
                print('!INFO Возможные причины: Неверный логин или пароль; нет связи с объектом')
                print('\n')
                self.table_entel.append('Conn. timed out or check credential')

    def checkError_Entel(self, page, ups_name):
        soup = BeautifulSoup(page, 'lxml')
        statuses = []
        statuses = soup.find_all(class_='Tabtext')
        statusOK = 'UPS Normal' or 'ИБП в норме'
        stat = list(statuses)
        try:
            if statusOK in str(stat):
                print('Status OK')
                dataString = f'{ups_name}'
                self.table_entel.append(dataString.ljust(30) + 'OK')
            else:
                print('!UPS Alarm: CHECK UPS ')
                dataString = f'{ups_name}'
                self.table_entel.append(dataString.ljust(30) + 'ALARM!')
        except Exception as ex:
            print('!ERROR Something went wrong! Unexpected result\n',ex)
            self.table_entel.append('Unexpected result')

    def getLpmPage(self):
        for i in self.ups_list['lpm']:
            combUrl = 'http://'+self.ups_list['lpm'][i]['ipaddres']+'/monitoring/ups_status.html'
            try:
                req = self.driver.get(url=combUrl)
                print(i,'!INFO connected. Loading web page...')
                # set timew to download js content on web page
                time.sleep(5)
                page = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                self.checkError_Lpm(page, i)
            except Exception as ex:
                print('!ERROR', ex)
                self.table_lpm.append('Conn. timed out')

    def checkError_Lpm(self, page, ups_name):
        soup = BeautifulSoup(page, 'lxml')
        page_text = soup.text
        print('!INFO parse data')
        statusOK = 'Онлайн'
        try:
            if statusOK in page_text:
                print('Status OK')
                dataString = f'{ups_name}'
                self.table_lpm.append(dataString.ljust(30)+'OK')
            else:
                print('!UPS Alarm: CHECK UPS')
                dataString = f'{ups_name}'
                self.table_lpm.append(dataString.ljust(30) + 'ALARM!')
        except Exception as ex:
            print('!ERROR Something went wrong! Unexpected result\n',ex)
            self.table_lpm.append('Unexpected result')


    def showReport(self):
        print('Status report:\n')
        for i in self.table_eaton:
            print(i)
        print('\n\n')
        for i in self.table_entel:        
            print(i)
        print('\n\n')
        for i in self.table_lpm:    
            print(i)
        print('\n\n')

if __name__ == '__main__':
    shark = GetUPS()
    shark.getEatonPage()
    shark.getEntelPage()
    shark.getLpmPage()
    shark.showReport()
    input('press enter to exit')


