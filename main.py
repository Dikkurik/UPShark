# Скрипт для опроса и получения данных ИБП фирмы Eaton по HTTP.

import requests, json
from bs4 import BeautifulSoup

print('Started UPShark script')

def getEatonPage():
    with open('ups_list.json', 'r+', encoding='utf-8') as file:
            ups_list = json.load(file)
    
    for i in (ups_list['eaton']):
        #Собираем URL 
        combUrl = f'http://{ups_list['eaton'][i]}/ups_propAlarms.htm'
        print(combUrl)
        try:
            req = requests.get(ups_list['eaton'][i])
            print(i, '*****')
            print('!INFO Successful connected to UPS at destination', ups_list['eaton'][i])
            req.encoding = "utf-8"
            page = req.text
            checkError_Eaton(page)
            print('\n')
        except:
            print(i, '!ERROR Connection timed out')
            print('\n')
    input('press enter to exit')

def checkError_Eaton(page: str) -> int:
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




if __name__ == '__main__':
   getEatonPage()


