# School-lib-tg-bot
A web scraping tool for extracting information from the website ukrlib.com.ua using aiohttp and requests_html. The data is organized into classes, authors, and books, including bios, book summaries, and audio links. The information is stored in a JSON file and is intended to be used in other applications.

This is a Python project that runs a Telegram bot for literature studies. The project consists of two files, `BOT_DB_.py` and `literatureClient.py`.

## BOT_DB_.py 🤖

This file uses the following libraries:

- `aiogram` for Telegram bot management
- `logging` for logging events
- `config` for token management

The file has functions for inline keyboard creation, user data handling, and callback query handling. It also imports and uses functions from `literatureClient.py`.

## [literatureClient.py](http://literatureclient.py/) 📚

This file has the following classes:

- `BSCH` for handling school books
- `DB` for handling book content

The file imports the following libraries:

- `pandas` for data handling
- `random` for randomization
- `telegraph` for creating HTML content

The `resource` folder contains JSON files for book content and school books.

## Requirements 🛠️

To run the project, the following libraries must be installed:

- `aiogram`
- `pandas`
- `telegraph`
- `json`

The project uses Telegram API and requires a Telegram Bot token to run. Detailed instructions on how to create a bot and obtain a token can be found on the Telegram Bot API documentation page.

# Українською

Це проект Python, який запускає бота Telegram для вивчення літератури. Проект складається з двох файлів, `BOT_DB_.py` та `literatureClient.py`.

## BOT_DB_.py 🤖

У цьому файлі використовуються наступні бібліотеки:

- `aiogram` для керування ботом Telegram
- `logging` для реєстрації подій
- `config` для керування токеном

Файл містить функції для створення вбудованої клавіатури, обробки даних користувача та обробки запитів зворотного виклику. Він також імпортує та використовує функції з `literatureClient.py`.

## [literatureClient.py](http://literatureclient.py/) 📚

У цьому файлі є наступні класи:

- `BSCH` для обробки шкільних книг
- `DB` для обробки вмісту книг

Файл імпортує наступні бібліотеки:

- `pandas` для обробки даних
- `random` для випадковості
- `telegraph` для створення HTML-контенту

У папці «resource» знаходяться файли JSON для вмісту книг та шкільних книг.

## Вимоги 🛠️

Для запуску проекту необхідно встановити наступні бібліотеки:

- `aiogram`
- `pandas`
- `telegraph`
- `json`

Проект використовує Telegram API та потребує токену бота Telegram для роботи. Детальні інструкції щодо створення бота та отримання токену можна знайти на сторінці документації Telegram Bot API.
</details>
