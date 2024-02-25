# Скрипт для опроса и получения данных ИБП фирмы Eaton по HTTP.

import requests, json
from bs4 import BeautifulSoup

print('Started UPShark script ver 1.02\n')

class GetUPS():
    def __init__(self):
        with open('ups_list.json', 'r+', encoding='utf-8') as file:
                self.ups_list = json.load(file)

    def getEatonPage(self):
        
        for i in (self.ups_list['eaton']):
            #Собираем URL 
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
        input('press enter to exit')

    def checkError_Eaton(self, page: str) -> int:
        #Объявляем объект супа с данными страницы
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

    def getEntelPage(self):
        for i in self.ups_list['entel']:
            combUrl = 'http://'+self.ups_list['entel'][i]['ipaddres']+'/Status.htm'
            try:
                req = requests.get(combUrl, 
                                    auth=(
                                    self.ups_list['entel'][i]['login'],
                                    self.ups_list['entel'][i]['password']
                                    ))
                print(i, '***** ENTEL')
                print('!INFO Successful connected to UPS at destination', self.ups_list['entel'][i]['ipaddres'])
                page = req.text
                self.checkError_Entel(page)

                
            except:
                print('Connection timed out')
                print(self.ups_list['entel'][i]['ipaddres'],
                      self.ups_list['entel'][i]['login'],
                      self.ups_list['entel'][i]['password'])
                
    def checkError_Entel(self, page):
        soup = BeautifulSoup(page, 'lxml')
        statuses = []
        statuses = soup.find_all(class_='Tabtext')
        statusOK = 'UPS Normal'
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
    shark.getEntelPage()
    input('press enter to exit')


