# Скрипт для опроса и получения данных ИБП фирмы Eaton по HTTP.

import requests, json
from bs4 import BeautifulSoup

print('Started UPShark script ver 1.02\n')

class GetUPS():
    # read UPS list from Json when object is called
    def __init__(self):
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        with open('ups_list.json', 'r+', encoding='utf-8') as file:
                self.ups_list = json.load(file)

    #Eaton functions
    def getEatonPage(self):
        for i in (self.ups_list['eaton']):
            #CombineURl URL 
            combUrl = 'http://'+self.ups_list['eaton'][i]+'/ups_propAlarms.htm'
            try:
                req = requests.get(combUrl)
                print(i, '***** EATON')
                print('!INFO Successful connected to UPS at destination', self.ups_list['eaton'][i])
                req.encoding = "utf-8"
                page = req.text
                self.checkError_Eaton(page)
                print('\n')
            except:
                print(i, '!ERROR Connection timed out')
                print('\n')

    def checkError_Eaton(self, page: str) -> int:
        #define soup object with page info
        soup = BeautifulSoup(page, 'lxml')
        errors = []
        errors = soup.find_all(class_='listline1')
        try:        
            if len(errors) > 0:
                print(f'Обнаружено {len(errors)} ошибок!')
                print('!!! UPS Alarm: CHECK UPS !!!')
                return len(errors)
            else:
                print('Status OK')
                return len(errors)
        except:
            print('Something went wrong! Unexpected result')

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
                        print(i, '***** ENTEL')
                        print('!INFO Successful connected to UPS at destination', self.ups_list['entel'][i]['ipaddres'])
                        self.checkError_Entel(page)
                        print('\n') 
                    else:
                        print('!ERROR authorization fail.')
                        print('!INFO Retry connect. Tries:', num)
                        num+=1
                               
            except:
                print('Connection timed out')
                print('Возможные причины: Неверный логин или пароль;\nНет связи с объектом')
                print('\n')
            
    def checkError_Entel(self, page):
        soup = BeautifulSoup(page, 'lxml')
        statuses = []
        print(page)
        statuses = soup.find_all(class_='Tabtext')
        statusOK = 'UPS Normal' or 'ИБП в норме'
        stat = list(statuses)
        try:
            if statusOK in str(stat):
                print('Status OK')
            else:
                print('!!! UPS Alarm: CHECK UPS !!!')
        except:
            print('Something went wrong! Unexpected result')



if __name__ == '__main__':
    shark = GetUPS()
    #shark.getEatonPage()
    shark.getEntelPage()
    input('press enter to exit')


