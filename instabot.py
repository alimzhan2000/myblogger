import requests
import telebot

token = "962351766:AAE_2ax6GANwka1ldGni2xMbV7-CPZboPEk"
bot = telebot.TeleBot(token)

url = "https://instagram9.p.rapidapi.com/api/instagram"
querystring = {"kullaniciadi":"tassygan","lang":"en"}
headers = {
    'x-rapidapi-host': "instagram9.p.rapidapi.com",
    'x-rapidapi-key': "44ede62fe1msh6bf135d3e2f37e8p1957e7jsn1f5a16437626"
    }

@bot.message_handler(commands = ['start'])
def start(message):
	bot.send_message(message.chat.id, 'Hello, enter your Instagram username. Without @ symbol.')
@bot.message_handler(content_types = ['text'])
def text(message):
	querystring = {"kullaniciadi":message.text,"lang":"en"}
	response = requests.request("GET", url, headers=headers, params=querystring)
	print(response.text)

bot.polling(none_stop=True)