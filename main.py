# Скрипт для опроса и получения данных ИБП фирмы Eaton, Entel, LPM по HTTP.

import requests, json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time

print ("""
 _   _ ____  ____  _                _              
| | | |  _ \/ ___|| |__   __ _ _ __| | __          
| | | | |_) \___ \| '_ \ / _` | '__| |/ /          
| |_| |  __/ ___) | | | | (_| | |  |   <           
 \___/|_|   |____/|_| |_|\__,_|_|  |_|\_\          

work in progress

Started UPShark script ver. 1.06              
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
        self.table_9sx = ['UPS 9sx report', '[_____________NAME___________][STATUS]']
        

    #Eaton functions
    def getEatonPage(self):
        for i in (self.ups_list['eaton']):
            #CombineURl URL 
            combUrl = 'http://'+self.ups_list['eaton'][i]+'/ups_propAlarms.htm'
            print(i, 'UPS EATON')
            try:
                req = requests.get(combUrl)
                print('    !INFO Successful connected to UPS at destination', self.ups_list['eaton'][i])
                req.encoding = "utf-8"
                page = req.text
                self.checkError_Eaton(page, i)
            except:
                print(i, '    !ERROR Connection timed out\n')
                self.table_eaton.append(str(i).ljust(30)+'Conn. timed out')

    def checkError_Eaton(self, page: str, ups_name: str):
        soup = BeautifulSoup(page, 'lxml')
        errors = []
        errors = soup.find_all(class_='listline1')
        try:        
            if len(errors) > 0:
                print(f'Detected {len(errors)} alarms!')
                print('    !ERROR UPS Alarm: CHECK UPS\n')
                dataString = f'{ups_name}'
                self.table_eaton.append(dataString.ljust(30)+f'ALARM! ({len(errors)})!')
                return len(errors)
            else:
                print('    Status OK\n')
                dataString = f'{ups_name}'
                self.table_eaton.append(dataString.ljust(30)+'OK')
                return len(errors)
        except Exception as ex:
            print('    !ERROR Something went wrong! Unexpected result:',ex,'\n')

    # Entel functions
    def getEntelPage(self):
        for i in self.ups_list['entel']:
            combUrl = 'http://'+self.ups_list['entel'][i]['ipaddres']+'/status.htm'
            
            try:
                num = 1
                status = True
                print(i, 'UPS ENTEL')
                while status:
                    req = requests.get(combUrl, 
                                    auth=(
                                    self.ups_list['entel'][i]['login'],
                                    self.ups_list['entel'][i]['password']
                                    ), headers=self.headers)
                    print('    !INFO connected. Status code:',req.status_code)

                    if num >= 10:
                        print (f'    !ERROR Connection to device was not succefull, tries: {num}\n')
                        self.table_entel.append(str(i).ljust(30)+f'Conn. error CODE: {req.status_code}')
                        status = False

                    if req.status_code == 200:
                        print('    !INFO Authorized. Parse data.')
                        status = False
                        page = req.text
                        
                        print('    !INFO Successful connected and authorized to UPS at destination', self.ups_list['entel'][i]['ipaddres'])
                        self.checkError_Entel(page, i)
                    
                    

                    else:
                        print(f'    !ERROR authorization or connection fail')
                        print(f'    !INFO Retry to connect. Tries:{num}')
                        num+=1
                        
                               
            except:
                print('    !ERROR Connection timed out')
                print('    !INFO Возможные причины: Неверный логин или пароль; нет связи с объектом\n')
                self.table_entel.append(str(i).ljust(30)+'Conn. timed out or check credential')

    def checkError_Entel(self, page, ups_name):
        soup = BeautifulSoup(page, 'lxml')
        statuses = []
        statuses = soup.find_all(class_='Tabtext')
        statusOK = 'UPS Normal' or 'ИБП в норме'
        stat = list(statuses)
        try:
            if statusOK in str(stat):
                print('    Status OK\n')
                dataString = f'{ups_name}'
                self.table_entel.append(dataString.ljust(30) + 'OK')
            else:
                print('    !ERROR UPS Alarm: CHECK UPS\n')
                dataString = f'{ups_name}'
                self.table_entel.append(dataString.ljust(30) + 'ALARM!')
        except Exception as ex:
            print('    !ERROR Something went wrong! Unexpected result:',ex,'\n')
            self.table_entel.append(dataString.ljust(30)+'Unexpected result')

    def getLpmPage(self):
        for i in self.ups_list['lpm']:
            combUrl = 'http://'+self.ups_list['lpm'][i]['ipaddres']+'/monitoring/ups_status.html'
            print(i, 'UPS LPM')
            try:
                req = self.driver.get(url=combUrl)
                print('    !INFO connected. Run container... Loading web page...')
                # set timer to download js content on web page
                time.sleep(5)
                page = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                self.checkError_Lpm(page, i)
            except Exception as ex:
                print('    !ERROR', ex,'\n')
                self.table_lpm.append(str(i).ljust(30)+'Conn. timed out')

    def checkError_Lpm(self, page, ups_name):
        soup = BeautifulSoup(page, 'lxml')
        page_text = soup.text
        print('    !INFO parse data')
        statusOK = 'Онлайн'
        try:
            if statusOK in page_text:
                print('    Status OK\n')
                dataString = f'{ups_name}'
                self.table_lpm.append(dataString.ljust(30)+'OK')
            else:
                print('    !ERROR UPS Alarm: CHECK UPS\n')
                dataString = f'{ups_name}'
                self.table_lpm.append(dataString.ljust(30) + 'ALARM!')
        except Exception as ex:
            print('    !ERROR Something went wrong! Unexpected result',ex,'\n')
            self.table_lpm.append(dataString.ljust(30), 'Unexpected result')

    def getEaton9sx(self):
        for i in self.ups_list['9sx']:
            # Eaton 9sx using https connection
            combUrl = 'https://'+self.ups_list['9sx'][i]['ipaddres']
            print(i, 'UPS 9SX')
            try:
                req = self.driver.get(url=combUrl)
                time.sleep(5)
                print('    !INFO connected. Run container... Loading web page...')

                # pass username and password then click login button
                self.driver.find_element(By.ID, 'loginpage-login-input-username').send_keys(self.ups_list['9sx'][i]['login'])
                self.driver.find_element(By.ID, 'loginpage-login-input-password').send_keys(self.ups_list['9sx'][i]['password'])
                self.driver.find_element(By.ID, 'loginpage-login-button-connexion').click()

                # set timer to download js content on web page
                time.sleep(5)
                page = self.driver.execute_script("return document.getElementById('home-alarm-list-pagination').innerHTML")
                self.checkError_9sx(page, i)
            except Exception as ex:
                print('    !ERROR', ex,'\n')
                self.table_9sx.append(str(i).ljust(30)+'Conn. timed out')

    def checkError_9sx(self, page, ups_name):
        print('    !INFO parse data')
        try:
            if 'No alarms to display' in page:
                dataString = f'{ups_name}'
                self.table_9sx.append(dataString.ljust(30)+'OK')
                print('    Status OK\n')
            else:
                dataString = f'{ups_name}'
                self.table_9sx.append(dataString.ljust(30)+'ALARM!')
                print('    !ERROR UPS Alarm: CHECK UPS\n')
        except Exception as ex:
            print('    !ERROR Something went wrong! Unexpected result',ex,'\n')
            self.table_lpm.append(dataString.ljust(30), 'Unexpected result')

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
        for i in self.table_9sx:    
            print(i)
        print('\n\n')

if __name__ == '__main__':
    shark = GetUPS()
    shark.getEatonPage()
    shark.getEntelPage()
    shark.getLpmPage()
    shark.getEaton9sx()
    shark.showReport()
    input('press enter to exit')


