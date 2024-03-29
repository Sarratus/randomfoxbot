import urllib.request
import aiohttp
import json
import pymorphy2
import qrcode
import re
import string

from PIL import Image, ImageDraw, ImageFont
from aiogram.types.input_file import InputFile

from pyzbar.pyzbar import decode, ZBarSymbol

from random import choice, random
from time import time
from datetime import datetime

from features.demotivatorCreator import intBox
from resources.links import             \
	pathToFoxLogo,      pathToFs,       \
	pathToSfd,          pathToSfd_bold  #
from misc import adminUserID

#  TODO: Очереди рандомного контента (для ускорения работы бота)
# wikiArticlesQueue = queue.Queue(maxsize=30)
# ytVideosQueue = queue.Queue(maxsize=30)


async def getRandomYoutubeVideo(ytApiKey):
	count = 1
	_random = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(3))

	urlData = "https://www.googleapis.com/youtube/v3/search?key=" \
	          f"{ytApiKey}&maxResults={count}&part=snippet&type=video&q={_random}"
	webURL = urllib.request.urlopen(urlData)
	data = webURL.read()
	encoding = webURL.info().get_content_charset('utf-8')
	results = json.loads(data.decode(encoding))

	# ytVideosQueue.put(f"https://www.youtube.com/watch?v={[i['id']['videoId'] for i in results['items']][0]}")

	return f"https://www.youtube.com/watch?v={[i['id']['videoId'] for i in results['items']][0]}"


# Возвращает ссылку на случайную статью из русскоязычной википедии
async def getRandomWikiArticle():
	wikiUrl = "https://ru.wikipedia.org/w/api.php?action=query&format=json&list=random&rnnamespace=0"

	async with aiohttp.ClientSession() as session:
		async with session.get(wikiUrl) as response:
			print("Wiki request is get")
			randomWikiArticle_json = await response.json()

			# wikiArticlesQueue.put(f"https://ru.wikipedia.org/wiki/?curid="
			#                       f"{randomWikiArticle_json['query']['random'][0]['id']}")

			return f"https://ru.wikipedia.org/wiki/?curid={randomWikiArticle_json['query']['random'][0]['id']}"


# Выбирает один ответ из n из сообщения пользователя (разделяет маркером "или")
def orDecider(userMessage):
	userMessage = userMessage.lower()

	# Парсинг строки по вариантам выбора
	listOfVariants = userMessage.split('или')
	fnd = re.compile(r'\b[\w \S-]+\b')

	for i in range(len(listOfVariants)):
		listOfVariants[i] = fnd.findall(listOfVariants[i])

	return choice(listOfVariants)[0]


# Случайно с равным шансов возвращает Да или Нет
def yesOrNot():
	return 'Да' if random() <= 0.5 else 'Нет'


morph = pymorphy2.MorphAnalyzer()


def randomRating(item):
	item = item if len(item) != 0 else 'это'

	if ' ' in item:
		item = item.split()
		if len(item) > 5:
			return "Слишком уж вы сложную вещь для оценивания выбрали. Лис не понимает :("
	else:
		item = [item]

	item = [morph.parse(i)[0] for i in item]

	ratingList = [
		[r"*0/10\!*" + '\n' + "_Лис хочет разорвать $$$ на куски, пожертвовав собой\. Мир не должен этого увидеть\.\.\._", 'accs'],
		[r"*1/10\!*" + '\n' + "_Кажется, Лису стало плохо\. Рыжее сердечко не выдержало такого убожества как $$$_", 'nomn'],
		[r"*2/10\!*" + '\n' + "_Лис нервно царапает $$$ и кусает, бегая вокруг\. Один Бог знает, что хорошее может быть в этой мерзости_", 'accs'],
		[r"*3/10\!*" + '\n' + "_После ежегодной лисячей вечеринки неделю назад осталось молоко\. Оно уже давно скисло, но выглядит до сих пор лучше, чем $$$_", 'nomn'],
		[r"*4/10\!*" + '\n' + "_Лис посмотрел на $$$ и отрыгнул вчерашнюю куриную косточку\. Почему? Он и сам не знает_", 'accs'],
		[r"*5/10\!*" + '\n' + "_Лис просто пробежал мимо по своим рыжим делам, не заметив $$$_", 'gent'],
		[r"*6/10\!*" + '\n' + "_Лис заинтересованно смотрит на $$$, но боится подойти\. Возможно, он почуял рыжую ауру_", 'accs'],
		[r"*7/10\!*" + '\n' + "_Лис радостно бегает вокруг $$$ и принюхивается, пытаясь определить, можно ли это съесть_", 'gent'],
		[r"*8/10\!*" + '\n' + "_Лис быстро подбежал, схватил кусочек $$$, и убежал\. Ему определённо понравилось_", 'gent'],
		[r"*9/10\!*" + '\n' + "_Вау\! Лис стал какать радугой при виде $$$\!\!\!_", 'gent'],
		[r"*10/10\!*" + '\n' + "_Все Лисы мира сбежались к $$$\. Кажется, лучше этого в глазах лисячьего сообщества нет ничего_", 'datv'],
	]
	_choice = choice(ratingList)

	inflectedItems = []
	for i in item:
		try:
			temp = i.inflect({f'{_choice[1]}'})[0]
		except:
			temp = i[0]
		inflectedItems.append(temp)

	rating = _choice[0].replace('$$$', ' '.join(inflectedItems))
	return rating


popList = [
	" ", "пе", "по", "пи", " ", "па", "пь ", "по", " ", "пa", "поо", "паа", "пи", " ", "пю",
	" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "
]


def randomPopGenerator(n):
	if n == 0:
		n = 1
	elif n > 100:
		n = 100

	_str = ''

	for _ in range(n):
		_str += choice(popList)

	_str = _str.strip()
	_str = re.sub(r'\s{2,}', ' ', _str)

	if _str == "" or _str == " ":
		_str = "попа"

	return _str


def randomPhrase():
	from resources.links import pathToRandomPhrases
	randomPhrases = open(pathToRandomPhrases, 'r', encoding='utf-8').read()

	randomPhrases = randomPhrases.split('\n\n\n')

	phrase = choice(randomPhrases).split('\n')

	if len(phrase) == 1:
		phrase.append(None)

	return phrase


def createQR(txt):

	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_M,
	    box_size=10,
	    border=4,
	)

	qr.add_data(txt)
	qr.make(fit=True)

	img = qr.make_image(fill_color="#f27122", back_color="#141414")
	img = img.convert('RGBA')

	foxLogo = Image.open(pathToFoxLogo)

	imWidth = img.width

	logoScale = 1/5.5   # от QR-кода
	foxLogo = foxLogo.resize(intBox(imWidth*logoScale, imWidth*logoScale))

	img.alpha_composite(foxLogo, dest=intBox(imWidth/2 - foxLogo.width/2, imWidth/2 - foxLogo.width/2))

	img = img.convert('RGB')
	photoPath = str(time()) + ".jpg"
	img.save(photoPath)

	img.close()
	foxLogo.close()

	return photoPath


async def uploadInputFileToTelegram(imgPath, bot):
	chatID = adminUserID
	img = InputFile(imgPath, filename='qr' + str(time()))

	imgMessage = await bot.send_photo(
		photo=img,
		chat_id=chatID,
		disable_notification=True,
	)

	imgFileId = imgMessage.photo[-1].file_id

	return imgFileId


def imageCorrection(img: Image, /, thresh: int=150, doInvert: bool=False) -> Image:
	from PIL.ImageChops import invert

	if doInvert:
		img = invert(img)

	fn = lambda x: 255 if x > thresh else 0
	img = img.convert('L').point(fn, mode='1')

	return img


def decodeQr(picPath):
	img = Image.open(picPath)

	thresh, doInvert = 150, True
	baseThresh = thresh

	for i in range(10):
		data = decode(img, symbols=[ZBarSymbol.QRCODE])

		if data:
			break

		img = imageCorrection(img, thresh=thresh, doInvert=doInvert)

		doInvert = not doInvert

		if i % 2 == 0 and i != 0:
			# i=2 -> baseThresh - 25*1
			# i=4 -> baseThresh + 25*1
			# i=6 -> baseThresh - 25*2
			# i=8 -> baseThresh + 25*2

			thresh = baseThresh + ((-1) ** ((i % 4) / 2)) * 25 * (i / 2)

	data = [decoded.data.decode('utf-8') for decoded in data]
	data = ',\n'.join(data)

	return data


def getCurrentTime() -> str:
	currTime = datetime.now().time()

	timezoneDifference: int = 5
	currHour: str = f"{(currTime.hour + timezoneDifference) % 24}"

	currMinute: str
	if currTime.minute < 10:
		currMinute = '0' + f'{currTime.minute}'
	else:
		currMinute = f'{currTime.minute}'

	currSec: str
	if currTime.second < 10:
		currSec = '0' + f'{currTime.second}'
	else:
		currSec = f'{currTime.second}'

	return currHour + ":" + currMinute + ":" + currSec


def textDrawer(drawer, txt, topPadding, fontSize, fontType: str='regular'):
	IPhoneScreenWidth, IPhoneScreenHeight = 640, 1136

	textColor = (255, 255, 255, 225)

	pathToFont: str
	if fontType == "bold":
		pathToFont = pathToSfd_bold
	else:
		pathToFont = pathToSfd

	_font = ImageFont.truetype(pathToFont, fontSize)

	priceTxtWidth, priceTxtHeight = drawer.textsize(txt, _font)
	priceTxtBox = intBox(IPhoneScreenWidth / 2 - priceTxtWidth / 2, topPadding,
	                     IPhoneScreenWidth / 2 + priceTxtWidth / 2, topPadding + priceTxtHeight)

	drawer.text(priceTxtBox, txt, font=_font, fill=textColor, align='center')


def fsCreator(timeTxt: str, priceTxt: str, nameTxt: str) -> str:
	priceTxt = priceTxt.replace(".", ",") + ' ₽'
	nameTxt = nameTxt.upper()

	fs = Image.open(pathToFs)

	IPhoneScreenWidth, IPhoneScreenHeight = 640, 1136

	topPadding_time = 7
	topPadding_price = 384
	topPadding_name = 478

	textIMG = Image.new('RGBA', (IPhoneScreenWidth, IPhoneScreenHeight), (0, 0, 0, 0))
	txtDrawer = ImageDraw.Draw(textIMG)

	fontSize_time = 22
	fontSize_price = 57
	fontSize_name = 27

	textDrawer(txtDrawer, timeTxt, topPadding_time, fontSize_time, fontType="bold")
	textDrawer(txtDrawer, priceTxt, topPadding_price, fontSize_price, fontType="bold")
	textDrawer(txtDrawer, nameTxt, topPadding_name, fontSize_name, fontType="regular")

	fs = Image.alpha_composite(fs, textIMG)

	IMGpath = str(time()) + ".png"
	fs.save(IMGpath)

	return IMGpath


def escapeMarkdown(text: str) -> str:
	return re.sub(r'([\\.\-!\#\(\)\[\]\{\}\"_\*>\+=\|]){1}', r'\\\g<1>', text)
