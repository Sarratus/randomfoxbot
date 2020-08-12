from primaryFunctions import getRandomWikiArticle, orDecider, \
	yesOrNot, randomRating, randomPopGenerator, getRandomYoutubeVideo, \
	createQR, uploadInputFileToTelegram, getCurrentTime
from demotivatorCreator import demotivatorCreator, txtPicCreator, isPic

from random import choice, randint

from aiogram import Bot, Dispatcher, types
from aiogram.types.input_media import InputMediaPhoto
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineQueryResultPhoto, \
	inline_keyboard
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor, markdown

from time import time
from asyncio import sleep

import os
import re

# https://sarratus.imgbb.com/ <- Картинки хранятся здесь

# Инициализация работы бота
bot_token = os.environ["bot_token"]
ytApiKey = os.environ["ytApiKey"]

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


helpImages = [
	'https://i.ibb.co/0Ydh6nV/qm.png',  # Вопросительный знак

	'https://i.ibb.co/T1Mwz1z/H.png',  # H

	'https://i.ibb.co/hDwK85z/E.png',  # E

	'https://i.ibb.co/L6nTC1v/L.png',  # L

	'https://i.ibb.co/vHzW7Rk/P.png'  # P
]

foxLogoPreview = 'https://i.ibb.co/0tzywHx/Unt22itled-1.png'

helpList = \
	[
		[
		'Введите один из запросов ниже:',

		'',

		'',

		'Основная функциональность бота заключена в inline-командах. '
		'Команды можно вводить как строчными, так и заглавными буквами. '
		'Некоторые из них описаны здесь'
		], [
		'Решение примеров:',

		'Математическое выражение c \"=\" на конце',

		'',

		"Введите математическое выражение, состоящее из чисел и простейших операций "
		"(Лис ещё только учится!!) типа \"*\", \"/\", \"+\", \"-\", оканчивающееся на знак \"=\" "
		"и Лис посчитает в столбик результат вычислений"
	], [
		'Случайная статья из Wikipedia:',

		'\"Wiki\"',

		'https://i.ibb.co/S6mcw2F/1200px-Wikipedia-logo-svg-svg.png',

		"Введите \"wiki\" или \"wikipedia\" в любом регистре, и Лис быстро сбегает до Вики и "
		"принесёт ссылку на случайную статью из русскоязычной Википедии"
	], [
		'Ответ на вопрос - \"Да\Нет\":',

		'Вопрос, заканчивающийся на \"?\"',

		'',

		"Введите любой вопрос, не содержащий \"или\" (желательно, на который можно ответить "
		"односложно, Лис ещё плохо понимает человечий и не может изъяснятся без переводчика, "
		"для большего погружения О_о), и бот ответит на него Да или Нет"
	], [
		'Выбор одного из вариантов:',

		'Список слов через \"или\"',

		'',

		"Введите любое количество слов через \"или\" и Лис, обнюхав, выберет одно из них"
	], [
		'Оценка чего-либо:',

		'\"rate\" и после то, что должен оценить бот',

		'',

		"Введите \"rate\" в любом регистре и через пробел то, что хотите отдать на оценку Лису. "
		"Он ответит вам в десятибальной шкале с небольшим милым пояснением"
	], [
		'Случайного видео из YouTube:',

		'\"yt\" или \"youtube\"',

		'https://i.ibb.co/RDttyBT/youtube-logo-png-2069.png',

		"Введите \"yt\" или \"youtube\", чтобы получить случайное видео с ютуба, которое в данный "
		"момент просматривает Лис"
	], [
		'QR-код:',

		'\"qr\" и после то, что вы хотите зашифровать',

		'',

		'Введите \"qr\" и то, что вы хотите видеть контентом qr-кода. Бот быстро и со вкусом создаст его'
	], [
		'Или в диалоге с ботом:',

		'',

		'',

		'Напишите в личные сообщения боту по тэгу @rnfoxbot или по ссылке t.me/rnfoxbot и введите одну '
		'из следующих команд'
	], [
		'Создание демотиватора',

		'\\демотиватор или \\демо, или \\demotivator',

		'',

		'Бот создаст демотиватор из картинки и двух строк текста, которые вы ему отправите. '
		'Все взаимодействия с ботом сопровождаются подсказками, так, что вы не потеряетесь'
	],
		# [
		# 	'Или в диалоге с ботом:',
		#
		# 	'',
		#
		# 	'',
		#
		# 	''
		# ], [
		# 	'Или в диалоге с ботом:',
		#
		# 	'',
		#
		# 	'',
		#
		# 	''
		# ]
	]

# TODO: Сделать информативный и красивый /start

@dp.inline_handler(regexp=r'(?i)^help$|^\s*$')
async def helpInlineHandler(inline_query: InlineQuery):
	items = [
		InlineQueryResultArticle(
			id=str(i),
			title=helpList[i][0],
			description=helpList[i][1],
			thumb_url=helpImages[i % 5],
			input_message_content=InputTextMessageContent(helpList[i][-1]))
		for i in range(len(helpList))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


@dp.inline_handler(regexp=r'(?i)^qr\b.+$')
async def qrInlineHandler(inline_query: InlineQuery):
	txt = re.search(r"(?i)qr\b\s+(.+)", inline_query.query).group(1)

	awaitingButton = inline_keyboard.InlineKeyboardButton(
		'Ожидайте...',
		callback_data='awaiting'
	)

	awaitingKeyboard = inline_keyboard.InlineKeyboardMarkup(row_width=1). \
		insert(awaitingButton)

	items = [
		InlineQueryResultPhoto(
			id=str(time() + 1),
			photo_url="https://i.ibb.co/n16zcs0/rnfoxbot-QR.jpg",
			thumb_url='https://i.ibb.co/KsbFqjG/rnfoxbot-QR.jpg',
			photo_width=200,
			photo_height=200,
			caption=
			markdown.italic("QR code с текстом") + '\n' +
			markdown.bold(f"\"{txt}\"") + '\n'
			,
			reply_markup=awaitingKeyboard,
			parse_mode='MarkdownV2'
		)
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


@dp.chosen_inline_handler(lambda chosen_inline_query: re.search(r"(?i)^qr\b.+$", chosen_inline_query.query))
async def some_chosen_inline_handler(chosen_inline_query: types.ChosenInlineResult):
	queryTxt = chosen_inline_query.query
	txt = re.search(r"(?i)qr\b\s+(.+)", queryTxt).group(1)

	voidInlineKeyboard = inline_keyboard.InlineKeyboardMarkup()

	qrCodePath = createQR(txt)
	imgID = await uploadInputFileToTelegram(qrCodePath, botToken=bot_token, bot=bot)

	await bot.edit_message_reply_markup(
		reply_markup=voidInlineKeyboard,
		inline_message_id=chosen_inline_query.inline_message_id
	)

	await bot.edit_message_media(
		media=InputMediaPhoto(media=imgID),
		inline_message_id=chosen_inline_query.inline_message_id
	)

	os.remove(qrCodePath)


# Обработчик запроса "Who am I?" Inline Query
@dp.inline_handler(regexp=r'(?i)who\s*am\s*i')
async def whoIAmInlineHandler(inline_query: InlineQuery):
	LGBTQKAplus = [
		"Гей", "Пидорас", "Лесбиян04ка", "FTM трансгендер", "MTF трансгендер",
		"Трансформер", "Мороженое \"Радуга\"", "Би", "Квирчик", "Апельсин", "Вертолёт АПАЧИ", "Big Poppa",
		"Small Joppa", "Агендер", "Асексуал", "Ким 5+", "Лох", "Валя Беляев", "Голубой", "Фанат зелёного гей флага",
		"забанены в твиттере"
	]

	answer = choice(LGBTQKAplus)
	print(answer)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Кто я из суперсемейки?',
			description=answer,
			thumb_url='https://i.ibb.co/PmrJZxc/1280px-Gay-Pride-Flag-svg.png',
			input_message_content=InputTextMessageContent(f"Вы {answer}!"))
	]
	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


doingTimersFrom = []
doingTimersFrom.clear()
@dp.inline_handler(lambda inline_query: re.search(r'(?i)stop\s+timer', inline_query.query))
async def some_callback_handler(inline_query: InlineQuery):
	userId = inline_query.from_user.id

	if userId in doingTimersFrom:
		print(userId, doingTimersFrom)
		doingTimersFrom.remove(userId)

		items = [
			InlineQueryResultArticle(
				id=str(time()),
				title="Завершаю таймер...",
				thumb_url=foxLogoPreview,
				input_message_content=InputTextMessageContent(""))
		]
	else:
		items = [
			InlineQueryResultArticle(
				id=str(time()),
				title="Не могу найти таймер",
				description="возможно, ни одного не запущено вами",
				thumb_url=foxLogoPreview,
				input_message_content=InputTextMessageContent(""))
		]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


@dp.chosen_inline_handler(lambda chosen_inline_query: re.search(r'(?i)timer\s+\d+', chosen_inline_query.query))
async def timerChangingHandler(chosen_inline_query: types.ChosenInlineResult):
	secCount = int(chosen_inline_query.query.strip().replace("timer", ""))
	userId = chosen_inline_query.from_user.id
	inlineMessageId = chosen_inline_query.inline_message_id

	if userId in doingTimersFrom:
		await bot.edit_message_text(
			text=f"Вы же уже запустили таймер?\nПодождите, пока он закончится...",
			inline_message_id=inlineMessageId
		)
		raise BlockingIOError("Таймер уже запущен этим пользователем")

	doingTimersFrom.append(userId)

	while secCount > 0:
		await bot.edit_message_text(text=f"{secCount}!", inline_message_id=inlineMessageId)

		# TODO: Сделать вычисление по времени, а не по вычитанию числа
		# TODO: Как-то оптимизировать этот код (хотя бы сократить и сделать более читаемым)
		secCount -= 1
		await sleep(1)

		if userId not in doingTimersFrom:
			break
	else:
		doingTimersFrom.remove(userId)

		currTime = getCurrentTime()
		doneButton = inline_keyboard.InlineKeyboardButton(
			'Закончен в ' + currTime,
			callback_data=f'something'
		)

		inlineKeyboard = inline_keyboard.InlineKeyboardMarkup(row_width=1).insert(doneButton)
		await bot.edit_message_text(text=f"Время истекло!",	inline_message_id=inlineMessageId)
		await bot.edit_message_reply_markup(reply_markup=inlineKeyboard,	inline_message_id=inlineMessageId)
		return

	await bot.edit_message_text(text=f"Таймер завершён досрочно", inline_message_id=inlineMessageId)


@dp.inline_handler(regexp=r'(?i)timer\s+\d+')
async def timerInlineHandler(inline_query: InlineQuery):
	secCount = int(inline_query.query.strip().replace("timer", ""))

	if secCount > 3600 or secCount < 1:
		articleTitle = "Таймер не будет запущен"
		isWrong = True
	else:
		articleTitle = 'Запускает таймер'
		isWrong = False

	awaitingButton = inline_keyboard.InlineKeyboardButton(
		'Таймер идёт...',
		callback_data='awaiting'
	)

	awaitingKeyboard = inline_keyboard.InlineKeyboardMarkup(row_width=1). \
		insert(awaitingButton)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title=articleTitle,
			description=f"на {secCount} секунд",
			reply_markup=awaitingKeyboard,
			thumb_url=foxLogoPreview,
			input_message_content=InputTextMessageContent(f"{secCount}!"))
	]
	if not isWrong:
		await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# Обработчик ответа Да\Нет на вопрос Inline Query
@dp.inline_handler(regexp=r'(?i)^(?=.*?\?)((?!или|or).)*$')
async def questionInlineQueryHandler(inline_query: InlineQuery):
	answer = yesOrNot()
	messToUser = markdown.bold(inline_query.query) + '\n' + markdown.italic(answer)
	print(messToUser)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Ответ',
			thumb_url=foxLogoPreview,
			input_message_content=InputTextMessageContent(messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


@dp.inline_handler(regexp=r'(?i)(.+\bили|or\b.+)+')
async def OrInlineQueryHandler(inline_query: InlineQuery):
	answer = orDecider(inline_query.query).capitalize()
	messToUser = markdown.bold(inline_query.query) + '\n' + markdown.italic(answer)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Лис выбрал слово...',
			thumb_url=foxLogoPreview,
			input_message_content=InputTextMessageContent(messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# Обработчик запроса случайной роры Inline Query
@dp.inline_handler(regexp=r'(?i)^\s*popa|попа\s+\d+')
async def popaInlineQueryHandler(inline_query: InlineQuery):
	_str = inline_query.query
	_str = re.sub(r'(?i)popa|попа', '', _str)
	num = int(_str.strip())

	answer = randomPopGenerator(num).strip().capitalize()
	messToUser = markdown.bold(answer)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Ророчка:',
			thumb_url=foxLogoPreview,
			input_message_content=InputTextMessageContent(messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# Обработчик запроса случайной роры Inline Query
@dp.inline_handler(regexp=r'(?i)num\s+-*\d+\s+-*\d+')
async def randNumInlineQueryHandler(inline_query: InlineQuery):
	num = [int(i) for i in inline_query.query.lower().replace("num", "").split()]

	randomNumber = str(randint(num[0], num[1]))
	messToUser = markdown.italic(f"Случайное число от {num[0]} до {num[1]}:") + '\n' + \
	             markdown.bold(f'{randomNumber}')
	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title=f'Случайное число от {num[0]} до {num[1]}:',
			description=randomNumber,
			thumb_url=foxLogoPreview,
			input_message_content=InputTextMessageContent(messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# Обработчик простейших математических выражений Inline Query
@dp.inline_handler(regexp=r'[\s\d\.\,\/\*\-\+\(\)]+=$')
async def calculationInlineQueryHandler(inline_query: InlineQuery):
	answer = str(eval(inline_query.query.replace("=", "").replace(",", ".")))
	messToUser = markdown.code(inline_query.query.replace(" ", "")) + markdown.code(answer)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Результат вычислений:',
			thumb_url='https://i.ibb.co/QmWSC1N/Untitled-2.png',
			description=answer,
			input_message_content=InputTextMessageContent(messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=50000000)


@dp.inline_handler(regexp=r'(?i)^\s*gay\b.+')
async def howMuchInlineQueryHandler(inline_query: InlineQuery):
	answer = randint(0, 100)

	_str = inline_query.query
	_str = re.sub(r'(?i)\s*gay\b\s+', '', _str)

	messToUser = markdown.italic(f"{_str} гей на {answer}%")

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title=f'Насколько {_str} гей?',
			description="нажми, если любишь маму",
			thumb_url='https://i.ibb.co/PmrJZxc/1280px-Gay-Pride-Flag-svg.png',
			input_message_content=InputTextMessageContent(message_text=messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=9999999999)


# Обработчик запроса оценки Inline Query
@dp.inline_handler(regexp=r'(?i)rate\b\b.*')
async def RateInlineQueryHandler(inline_query: InlineQuery):
	item = inline_query.query.lower().replace("rate", '').strip()
	messToUser = randomRating(item)

	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Оценка от Лиса',
			description='Лисик вынес окончательный вердикт!',
			thumb_url=foxLogoPreview,
			input_message_content=InputTextMessageContent(messToUser, parse_mode='MarkdownV2'))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# Обработчик запроса случайного видео с YouTube Inline Query
@dp.inline_handler(regexp=r'(?i)yt|youtube')
async def youtubeInlineQueryHandler(inline_query: InlineQuery):
	randomYoutubeVideo = await getRandomYoutubeVideo(ytApiKey)
	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Случайное видео с YouTube',
			description='Рекомендация от Лиса',
			thumb_url='https://i.ibb.co/RDttyBT/youtube-logo-png-2069.png',
			input_message_content=InputTextMessageContent(randomYoutubeVideo))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# Обработчик запроса случайной статьи Википедии Inline Query
@dp.inline_handler(regexp=r'(?i)wiki|wikipedia')
async def wikiInlineQueryHandler(inline_query: InlineQuery):
	randomWikiArticle = await getRandomWikiArticle()
	items = [
		InlineQueryResultArticle(
			id=str(time()),
			title='Случайная статья из Википедии',
			description='Рекомендация от Лиса',
			thumb_url='https://i.ibb.co/S6mcw2F/1200px-Wikipedia-logo-svg-svg.png',
			input_message_content=InputTextMessageContent(randomWikiArticle))
	]

	await bot.answer_inline_query(inline_query.id, results=items, cache_time=0)


# @dp.message_handler(regexp='(?i)id')
# async def idMessageHandler(message: types.Message):
# 	print(message.chat.id)


############################ FSM для генерации демотиваторов #################################


# States
class Form(StatesGroup):
	pic = State()
	header = State()
	subtitle = State()
	generationDemo = State()
	headerChanging = State()
	subtitleChanging = State()


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', regexp=r'(?i)/отмена|/cancel|ʘтмена')
async def cancelHandler(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return

	async with state.proxy() as data:
		try:
			if '.' in data['pic']:
				os.remove(data['pic'])
		except:
			pass

	await state.finish()
	await message.answer('Отменено.')


@dp.message_handler(filters.Text(equals="Демотиватор"), state=None)
@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'(?i)demotivator|demo|демо|демотиватор$']), state=None)
async def demoCallingHandler(message: types.Message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, row_width=2)
	markup.add("Демотиватор")
	markup.insert("Пρопустить подзаголовок")
	markup.add("ʘтмена")

	await Form.pic.set()
	await message.answer("Отправь картинку, которую хотел бы видеть в демотиваторе", reply_markup=markup)


@dp.message_handler(content_types=['photo'], state=Form.pic)
async def picDemoHandler(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		photoName = str(time()) + ".jpg"
		data['pic'] = photoName
		await message.photo[-1].download(photoName)

	await Form.header.set()
	await message.answer("Что будет в заголовке демотиватора?")


@dp.message_handler(state=Form.header)
async def headerDemoHandler(message: types.Message, state: FSMContext):
	if message.text:
		await state.update_data(header={"text": message.text, "message": message})

		await Form.subtitle.set()
		await message.answer("А в подзаголовке?")
	else:
		await message.reply("Не похоже на текст...")


@dp.message_handler(state=Form.headerChanging)
async def headerChangingDemoHandler(message: types.Message, state: FSMContext):
	if message.text:
		await state.update_data(header={"text": message.text, "message": message})

		await Form.generationDemo.set()
		await demoFinisher(message, state)
	else:
		await message.reply("Не похоже на текст...")


@dp.message_handler(state=Form.subtitle)
async def subtitleDemoHandler(message: types.Message, state: FSMContext):
	if message.text:
		if message.text == "Пρопустить подзаголовок":
			async with state.proxy() as data:
				data['subtitle'] = None
		else:
			async with state.proxy() as data:
				data['subtitle'] = {"text": message.text, "message": message}

		await Form.generationDemo.set()
		await demoFinisher(message, state)
	else:
		await message.reply("Не похоже на текст...")


@dp.message_handler(state=Form.subtitleChanging)
async def subtitleChangingDemoHandler(message: types.Message, state: FSMContext):
	if message.text:
		if message.text == "Пρопустить подзаголовок":
			async with state.proxy() as data:
				data['subtitle'] = None
		else:
			async with state.proxy() as data:
				data['subtitle'] = {"text": message.text, "message": message}

		await Form.generationDemo.set()
		await demoFinisher(message, state)
	else:
		await message.reply("Не похоже на текст...")


@dp.message_handler(state=Form.generationDemo)
async def demoFinisher(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			subTxt = data['subtitle']['text']
		except:
			subTxt = None

		try:
			hTxt = data['header']['text']
			txtPic = txtPicCreator(hTxt=hTxt, subTxt=subTxt, picPath=data['pic'])
		except ValueError as exception:
			messageToUser = exception.args[0]
			exceptionIn = exception.args[1]

			if exceptionIn == "subtitle":
				messageWhichContainsTooLongText = data['subtitle']['message']
				await Form.subtitleChanging.set()

			elif exceptionIn == "header":
				messageWhichContainsTooLongText = data['header']['message']
				await Form.headerChanging.set()

			await messageWhichContainsTooLongText.reply(messageToUser + "\n" + "Повторите ввод:")

			raise

	demPath = demotivatorCreator(picPath=data['pic'], txtPic=txtPic)

	# Проверка: сгенерировался ли демотиватор
	if '.' not in demPath:
		await message.answer(demPath)
	else:
		with open(demPath, 'rb') as photo:
			await bot.send_photo(message.chat.id, photo, caption='Демотиватор готов!')
		os.remove(demPath)

	os.remove(data['pic'])

	await state.finish()


########################## FSM для генерации демотиваторов #############################

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)

########################################################################################

# Спасибо Дино :3