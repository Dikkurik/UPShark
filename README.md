# UPShark скрипт

**UPShark** Скрипт для опроса ИБП фирмы Eaton серии 9000, Entel

Работает при помощи BeautifulSoup, Requests.
Приемуществом скрипта является то, что происходит загрузка легковесного HTM документа по прямому его адресу. 
## Принцип работы 

При инициализации класса GetUPS() происходит чтение из Json файла данных о всех внесенных ибп.
Далее вызываются методы класса getEatonPage() и getEntelPage()
### Парсинг Eaton
 - Из Json файла берется имя и адрес с портом ИБП Eaton;
 - Происходит иттерация каждого элемента словаря из Json файла;
 - При помощи Requests получается HTM-документ с ИБП по адресу *ipaddres:**port**/ups_propAlarms.htm*;
    > Если подключится к ИБП не удалось выдается ошибка "!ERROR Connection timed out"
 - Далее HTM документ парсится в методе класса **checkError_Eaton()** на наличие HTML-тэга, с классом listline1, в котором находятся информация об ошибках;
    > В тэге с классом listline0 находится шапка таблицы, возможно есть классы выше listline1,
        но программа проверяет только listline1  (т.к. по логике другие тэги уже не нужны - на ИБП уже есть аварии.)
 - Далее в пустой список добавляются вся информация из искомого тэга и их кол-во
 - Если длинна списка больше 0 выдается статус "!!! UPS Alarm: CHECK UPS !!!", а если 0 "Status OK"
 
### Парсинг Entel
 - Из Json файла берется имя, адрес с портом, логин и пароль до ИБП Entel;
 - Происходит иттерация каждого элемента словаря из Json файла;
 - При помощи Requests получается HTM-документ с ИБП по адресу *ipaddres:**port**/Status.htm*;
    > Используется Basic html аутентификация.
    > Если подключится к ИБП не удалось выдается ошибка "!ERROR Connection timed out"
 - Далее HTM документ парсится в методе класса **checkError_Entel()** на наличие в тегах, с классом Tabtext, внутри тегов с совпадние со значением в строке 'UPS Normal' если совпадние обнаружена возвращается Status Ok, если нет - выдается статус "!!! UPS Alarm: CHECK UPS !!!";

### Парсинг LPM 


## Структра Json-файла.
Структура Json-файла. На даннный момент структура Json файла выглядит так:

{"eaton":{
    "Какой-то ИБП":"192.168.1.0:1234"
     *след. элемент*},

"entel":
   {"Какой-то ИБП":{
    "ipaddres":"10.0.0.1",
    "login":"admin",
    "password":"admin "
    }, {След элемент}
    
    }
    }