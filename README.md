# muon_nodes_checker
## Описание проекта:
Телеграм бот, который проверяет статус Muon network узла, также есть возможность запросить количество активных, неактивных и общее количество узлов в сети.

## Команды:
- **/start** - Initializing the bot
- **/status** - Muon Nodes Status.
- **/help** - Information on bot commands
- **/muon** - About Muon Network
- **/about** - About the author and the project.


## Версия и дата:
- **Версия**: Muon Nodes checker 1.1.0
- **Дата**: 26.06.2023

## Обновления:

- В данном релизе добавлена команда **/status**, которая отображает:
	1. Общее количество узлов
	2. Количество активных узлов 
	3. Количество неактивных узлов. 
- Исправлен вывод полной информации о узле, в том числе :
	1. Реальный аптайм ноды в процентном соотношение. 
	2. ID узла
	3. Статус узла, Сеть.
	4. Скрыты такие поля как Node, Staker и Peer id.


# Как запустить проект:

```sh
git clone git@github.com:AlexBesedin/muon_nodes_checker.git
cd muon_nodes_checker
```
Создать файл с переменными окружения .env
```sh
touch .env
```
Пример содержимого файла .env:
```sh
TELEGRAM_TOKEN=6266692408fdsfsdf23123das
```
Установите docker и docker-compose:
```sh
sudo apt install docker.io 
sudo apt install docker-compose
```
Запустите контейнер:
```sh
sudo docker-compose up -d --build

```

Ссылка на бота: https://t.me/MuonNodes_bot
