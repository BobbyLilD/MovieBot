import array

import telebot
from telebot import types
import urllib.request
import urllib.parse
from selenium import webdriver
from lxml import html

bot = telebot.TeleBot('1766116714:AAGJyONFIFHy-X1T3Nj4V16D487GliyaTXw')

global driver
driver = webdriver.Firefox()
global infoDivs
infoDivs = None
global sourceForPhotos
sourceForPhotos = None


def getBudgetInfo(soup):
    data = []
    for i in soup:
        if i.xpath('./div')[0].xpath('./text()')[0] == "Бюджет":
            budget = i.xpath('./div')[1].xpath('./a/text()')[0]
            print("Found Budget")
            soup.remove(i)
            data.append("Бюджет - " + budget)
        elif i.xpath('./div')[0].xpath('./text()')[0] == "Маркетинг":
            marketing = i.xpath('./div')[1].xpath('./a/text()')[0]
            print("Found Marketing")
            soup.remove(i)
            data.append("Маркетинг - " + marketing)
        elif i.xpath('./div')[0].xpath('./text()')[0] == "Сборы в США":
            USAbox = i.xpath('./div')[1].xpath('./a/text()')[0]
            print("Found USA box office")
            soup.remove(i)
            data.append("Сборы в США - " + USAbox)
        elif i.xpath('./div')[0].xpath('./text()')[0] == "Сборы в мире":
            worldwide = i.xpath('./div')[1].xpath('./a/text()')[0]
            print("Found Worldwide box office")
            soup.remove(i)
            data.append("Сборы в мире - " + worldwide[worldwide.find('=') + 1:])
        elif i.xpath('./div')[0].xpath('./text()')[0] == "Сборы в России":
            russia = i.xpath('./div')[1].xpath('./a/text()')[0]
            print("Found Russia box office")
            soup.remove(i)
            data.append("Маркетинг - " + russia)
    return data

def getGenre(soup,data):
    for i in soup:
        if i.xpath('./div')[0].xpath('./text()')[0] == "Жанр":
            genres = i.xpath('./div')[1].xpath('./div/a')
            print("Found Genres")
            res = []
            for j in genres:
                genre = j.xpath('./text()')[0]
                res.append(genre)
            soup.remove(i)
            data.append("Жанр - " + ', '.join(res))

    return data


def getShots(soup):
    link = soup.xpath('//div[@data-tid="5c85b95c"]/a[contains(@href, "images")]/@href')
    if len(link) > 0:
        url_new = "https://www.kinopoisk.ru" + link[0]
        print(url_new)
        driver.get(url_new)
        soup = html.fromstring(driver.page_source)
        photoTableRows = soup.xpath('//table[@class="js-rum-hero fotos fotos2"]/tbody/tr')
        print(photoTableRows)
        data = []
        for i in range(len(photoTableRows)):
            if i > 1:
                break
            columns = photoTableRows[i].xpath('./td')
            for j in columns:
                imageLink = j.xpath('./a/img/@src')[0]
                data.append(imageLink[8:])
        return data
    return None


def getInfoList(soup):
    divs = soup.xpath('//div[@data-tid="a25321e6"]')
    print(divs)
    return divs


def getAlternateName(soup, data):
    name = soup.xpath('//span[@class="styles_originalTitle__31aMS"]/text()')
    if len(name) > 0:
        data.append(f'Альтернативное название фильма - {name[0]}')
    return data


def getPoster(soup):
    poster = soup.xpath('//a[@class="styles_posterLink__1agYl"]/img/@src')
    if poster is not []:
        return poster[0][2:]
    else:
        return None


def getProductionYear(soup, data):
    for i in soup:
        if i.xpath('./div')[0].xpath('./text()')[0] == "Год производства":
            yearOfProdution = i.xpath('./div')[1].xpath('./a/text()')[0]
            print("Found YearOfProd")
            soup.remove(i)
            data.append("Год производства - " + yearOfProdution)

    return data


def getCountry(soup, data):
    for i in soup:
        if i.xpath('./div')[0].xpath('./text()')[0] == "Страна":
            countries = i.xpath('./div')[1].xpath('./a')
            print("Found Countries")
            res = []
            for j in countries:
                country = j.xpath('./text()')[0]
                print(country)
                res.append(country)
            soup.remove(i)
            data.append("Страна - " + ', '.join(res))

    return data


def getSlogan(soup, data):
    for i in soup:
        if i.xpath('./div')[0].xpath('./text()')[0] == "Слоган":
            slogan = i.xpath('./div')[1].xpath('./div/text()')[0]
            print("Found Slogan")
            soup.remove(i)
            if slogan != '-':
                data.append("Слоган - " + slogan)

    return data


def getDirector(soup, data):
    for i in soup:
        if i.xpath('./div')[0].xpath('./text()')[0] == "Режиссер":
            directors = i.xpath('./div')[1].xpath('./a/text()')
            print("Found Director")
            soup.remove(i)
            data.append("Режиссер - " + ','.join(directors))

    return data


def soupParseWantedName(soup):
    link = soup.xpath('//div[@class="element most_wanted"]/div[@class="info"]/p/a/@href')
    if len(link) > 0:
        print(link)
        url_new = "https://www.kinopoisk.ru" + link[0]
        return url_new
    else:
        return None


def sendOptionalMessage(message):
    btnBudget = types.InlineKeyboardButton(text="Бюджет и сборы", callback_data="Budget")
    btnShots = types.InlineKeyboardButton(text="Кадры из фильма", callback_data="Shots")
    btnNewMovie = types.InlineKeyboardButton(text="Найти новый фильм", callback_data="New")
    rows = []
    rows.append([btnBudget])
    rows.append([btnShots])
    rows.append([btnNewMovie])
    key = types.InlineKeyboardMarkup(keyboard=rows)
    bot.send_message(message, "Выбери дальнейшее действие", reply_markup=key)

def send_start_option(message):
    btnNewMovie = types.InlineKeyboardButton(text="Найти фильм", callback_data="New")
    key = types.InlineKeyboardMarkup()
    key.add(btnNewMovie)
    bot.send_message(message, "Нажми на кнопку, чтобы найти информацию о любом фильме!", reply_markup=key)


@bot.callback_query_handler(func=lambda c: True)
def optionalResponse(c):
    print("InlineResponse")
    if c.data == "Budget":
        if infoDivs is not None:
            data = getBudgetInfo(infoDivs)
            bot.send_message(c.message.chat.id, "\n".join(data))
            sendOptionalMessage(c.message.chat.id)
        else:
            bot.send_message(c.message.chat.id, "Упс, что-то пошло не так(")
            sendOptionalMessage(c.message.chat.id)
        # ОТОБРАЖЕНИЕ БЮДЖЕТА И СБОРОВ
    elif c.data == "Shots":
        if sourceForPhotos is not None:
            data = getShots(sourceForPhotos)
            if data is not None:
                photos = [types.InputMediaPhoto(i) for i in data]
                bot.send_media_group(c.message.chat.id, photos)
                sendOptionalMessage(c.message.chat.id)
            else:
                bot.send_message(c.from_user.id, "Упс, что-то пошло не так(")
                sendOptionalMessage(c.message.chat.id)
        # ОТОБРАЖЕНИЕ СКРИНОВ ИЗ ФИЛЬМА
    elif c.data == "New":
        print('New movie trigger')
        bot.send_message(c.message.chat.id, 'Введи название фильма!')
        bot.register_next_step_handler(c.message, get_movies_info)


@bot.message_handler(commands=['start'])
def send_start_response(messsage):
    bot.send_message(messsage.from_user.id, f'Привет, {messsage.from_user.first_name} !')
    send_start_option(messsage.chat.id)


@bot.message_handler(commands=['help'])
def send_help_response(message):
    send_start_option(message.chat.id)


@bot.message_handler(content_types=['text'])
def send_random_text_response(message):
    send_start_option(message.chat.id)


@bot.message_handler(commands=['new'])
def send_new_response(messsage):
    bot.send_message(messsage.from_user.id, 'Введи название фильма!')
    bot.register_next_step_handler(messsage, get_movies_info)


def get_movies_info(message):
    req = message.text
    res_url = "https://www.kinopoisk.ru/index.php?kp_query="
    driver.get(res_url + urllib.parse.quote_plus(req))
    soup = html.fromstring(driver.page_source)
    infoLink = soupParseWantedName(soup)
    if infoLink is not None:
        driver.get(infoLink)
        # ЗАМЕНА НА LXML
        soup = html.fromstring(driver.page_source)
        global sourceForPhotos
        sourceForPhotos = soup
        global infoDivs
        infoDivs = getInfoList(soup)
        if infoDivs is not []:
            data = []
            data = getAlternateName(soup, data)
            poster = getPoster(soup)
            data = getProductionYear(infoDivs, data)
            data = getCountry(infoDivs, data)
            data = getGenre(infoDivs, data)
            data = getSlogan(infoDivs, data)
            data = getDirector(infoDivs, data)

            if poster is not None:
                bot.send_photo(message.from_user.id, poster)
            if data:
                bot.send_message(message.from_user.id, "\n".join(data))
                sendOptionalMessage(message.chat.id)
        else:
            bot.send_message(message.from_user.id, "Упс, что-то пошло не так( \n"
                                                   "Попробуй ещё раз ввести название фильма!")
            bot.register_next_step_handler(message, get_movies_info)

    else:
        bot.send_message(message.from_user.id, "Прости, я не понимаю, о каком фильме ты говоришь( \n"
                                               "Можешь, пожалуйста, перефразировать?")
        bot.register_next_step_handler(message, get_movies_info)


bot.polling(none_stop=True)
