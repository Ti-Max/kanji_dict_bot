# Kanji mnemonics dictionary
This is a Telegram bot made with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

[WaniKani anki deck](https://ankiweb.net/shared/info/2072613354) was used as a dictionary source.

~~The bot is ***maybe*** live [@wanikani_cards_bot](https://t.me/wanikani_cards_bot) <br>
To start, simply send one single kanji or radical~~

# Features
* Search Meaning & Mnemonics of *2048* Kanji
* Search Meaning & Mnemonics of *481* Radical
* ~~Search Meaning & Mnemonics of *5352* Vocabulary~~ (comming soon)
* Break down Kanji into individual radicals with one button click

# Instructions 
* Fill `.env` with the telegram bot `TOKEN` that [@BotFather](https://t.me/BotFather) gave you
* Run `poetry install` to install python dependencies
* Run `poetry run python3 kanji_dict_bot/telegram_bot.py` to start telegram bot
