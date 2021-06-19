import telebot
import urllib.request
import urllib.parse
from selenium import webdriver
from lxml import html
bot = telebot.TeleBot('1766116714:AAGJyONFIFHy-X1T3Nj4V16D487GliyaTXw')

global driver
driver = webdriver.Firefox()

def getAlternateName(soup, data):
    name = soup.xpath('//span[@class="styles_originalTitle__31aMS"]/text()')
    if len(name) > 0:
        data.append(f'Альтернативное название фильма - {name[0]}')
    return data

def getPoster(soup):
    poster = soup.xpath('//a[@class="styles_posterLink__1agYl"]/img/@src')[0]
    return poster[2:]

def getProductionYear(soup, data):
    div = soup.xpath('//div[@data-tid="a189db02"]/a/text()')[0]
    data.append(f'Год производства - {div}')

    return data

def getCountry(soup,data):
    div = soup\
        .xpath('//div[@data-tid="df943f2f"]/a[@data-tid="60f1c547"][starts-with(@href, "/lists/navigator/country")]')
    res = []
    for i in div:
        res.append(i.xpath("./text()")[0])
    resString = "Страна производства - " + ", ".join(res)
    data.append(resString)
    return data

def getSlogan(soup, data):
    div = soup.xpath('//div[@data-tid="849d1be2"]/div/text()')
    if len(div) > 0:
        data.append(f"Слоган - {div[0]}")

    return data


def soupParseWantedName(soup):
    link = soup.xpath('//div[@class="element most_wanted"]/div[@class="info"]/p/a/@href')[0]
    print(link)
    url_new = "https://www.kinopoisk.ru" + link
    return url_new

@bot.message_handler(commands=['start'])
def send_start_response(messsage):
    bot.send_message(messsage.from_user.id, f'Привет, {messsage.from_user.first_name} ! \n '
                                            f'Напиши /new, чтобы найти информацию о любом фильме!')

@bot.message_handler(commands=['help'])
def send_help_response(message):
    bot.send_message(message.from_user.id, 'Напиши /new, чтобы найти информацию о любом фильме!')

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
    driver.get(infoLink)
    # ЗАМЕНА НА LXML
    soup = html.fromstring(driver.page_source)

    data = []
    data = getAlternateName(soup, data)
    poster = getPoster(soup)
    data = getProductionYear(soup, data)
    data = getCountry(soup, data)
    data = getSlogan(soup, data)

    bot.send_photo(message.from_user.id, poster)
    bot.send_message(message.from_user.id, "\n".join(data))


bot.polling(none_stop=True)

