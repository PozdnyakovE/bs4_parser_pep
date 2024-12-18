# Проект парсера документации python и PEP
# Автор: Поздняков Евгений (https://github.com/PozdnyakovE)
## Описание
Парсер информации со страниц сайта Python
### Как развернуть локально:
Клонируйте репозиторий к себе на компьютер:
```
git clone https://github.com/PozdnyakovE/bs4_parser_pep.git
```
В корневой папке нужно создать виртуальное окружение и установить зависимости.
```
python -m venv venv
```
```
pip install -r requirements.txt
```
### сменить директорию на папку ./src/
```
cd src/
```
### запустить файл main.py с необходимыми параметрами
```
python main.py [вариант парсера] [аргументы]
```
### Параметры запуска парсера
- whats-new   
Вывод списка изменений в python (Что нового?).
```
python main.py whats-new [аргументы]
```
- latest_versions
Вывод версий Python и ссылок на документацию.
```
python main.py latest-versions [аргументы]
```
- download   
Загрузка архива с документацией Python.
```
python main.py download [аргументы]
```
- pep
Парсер всех документов PEP (подсчет количества всех PEP, количества PEP в каждом статусе). 
```
python main.py pep [аргументы]
```
### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache
Очистка кеша перед выполнением парсинга.
```
python main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python main.py [вариант парсера] -o file
```