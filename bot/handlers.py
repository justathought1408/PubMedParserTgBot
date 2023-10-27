#parsing
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
ua = UserAgent()

# aiogram
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message, CallbackQuery, ParseMode

# built-in
from time import sleep

# modules
from config import dp, bot

# translate (googletrans==3.1.0a0)
from googletrans import Translator

parsing = True

@dp.message_handler(Command("start"))
async def start_command(message: Message):
	await message.answer("Введите запрос с командой /q. Пример:\n\n/q diabetes\n\nЧтобы остановить запросы, введите команду /stop")


@dp.message_handler(Command("q"))
async def parsing_query(message: Message):
	global parsing
	parsing = True

	pagination_count = 0

	article_count = 1

	for pagination_count in range(1, 6):
		headers = { "User-Agent": ua.random, } # Заголовки в Метаданных

		request = message.text.replace("/q ", "") # Убрать команду из сообщения для запроса

		# Ссылка на список статей, в которых доступен abstract
		url = f"https://pubmed.ncbi.nlm.nih.gov/?term={request}&filter=simsearch1.fha&page={pagination_count}"

		main_url = "https://pubmed.ncbi.nlm.nih.gov" # Основной адрес сайта


		response = requests.get(url, headers = headers) # Запрос к странице

		soup = BeautifulSoup(response.text, "lxml") # Парсинг html-кода, чтобы найти DOM-элементы

		data_links = soup.find_all("a", class_="docsum-title") # Собрать все ссылки на статьи в словарь

		translator = Translator()

		# Переход по ссылкам
		for link in data_links:
			sleep(3) # Перерыв между запросами в 3 сек

			link = link.get("href") # Получить значение атрибута 'href' у каждого тэга 'a'
			link = main_url + link.strip() # Добавить перед относительной ссылкой основной адрес сайта, чтобы получилась полная ссылка на статью

			article_response = requests.get(link, headers = headers) # Запрос к каждой из страниц со статьями

			article_soup = BeautifulSoup(article_response.text, "lxml") # Парсинг каждой из страниц со статьями

			article_title = article_soup.find("h1", class_="heading-title") # Найти заголовок в каждой статье
			article_title = article_title.text # Заголовок статьи
			article_title_translated = translator.translate(article_title, src = "en", dest = "ru") # Заголовок статьи
			article_title_translated = article_title_translated.text

			article_abstract = ""
			article_abstract_translated = ""

			# Найти все параграфы в блоке Abstract
			article_abstract_paragraphs = article_soup.find("div", class_="abstract-content").find_all("p")

			# Добавить все параграфы в одну строку
			for article_p in article_abstract_paragraphs:
				if parsing:
					article_abstract += article_p.text + "\n"

					# Переведённый Abstract
					article_abstract_translated += translator.translate(article_p.text, src = "en", dest = "ru").text

					# Ответ бота
					# Если у бота есть закончился лимит на переводы, то вернуть вариант без перевода заголовка
					if len(article_abstract.strip()) < 4096 and len(article_abstract_translated) < 4096:
						await message.answer(
							# Номер статьи (с конца)
							str(article_count) + 

							# Заголовок (оригинал)
							"\n\n\n" + "* Title:" + 
							"\n\n" + article_title.strip() +
				
							# Abstract
							"\n\n\n" + "* Abstract:" +
							"\n\n" + article_abstract.strip(),
				
							# parse_mode = "HTML"
						)

						sleep(2) # Перерыв между запросами в 2 сек

						await message.answer(
							f"👆Перевод статьи {article_count}:"

							# Перевод заголовка статьи
							"\n\n\n" + "* Заголовок (Перевод):" + 
							"\n\n" + article_title_translated.strip() + 

							# Перевод abstract
							"\n\n\n" + "* Абстракт (Перевод):" 
							"\n\n" + article_abstract_translated
						)
					else:
						await message.answer(
							# Номер статьи (с конца)
							str(article_count) + 

							# Заголовок (оригинал)
							"\n\n\n" + "* Заголовок:" + 
							"\n\n" + article_title.strip() +

							# Перевод заголовка статьи
							"\n\n\n" + "* Заголовок (Перевод):" + 
							"\n\n" + article_title_translated.strip() + 
					
							# Abstract
							"\n\n\n" + "* Abstract:" +
							"\n\n" + "Abstract не помещается в сообщение Telegram (символов больше 4096).",
							"\n\n" + f"Ссылка на статью: {link}"
					
							# parse_mode = "HTML"
						)
				else:
					break

				article_count += 1 # Счётчик статей (с конца)

				if not parsing:
					break
			
			if not parsing:
				break

		if not parsing:
			break



@dp.message_handler(Command("stop"))
async def stop(message: Message):
	global parsing
	parsing = False
	await message.answer("Запросы остановлены.")
	await message.answer("Запросы остановлены.")