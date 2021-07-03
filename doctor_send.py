import telegram

token='1828719216:AAFfUolgmxsLZ7WQrsEujxz8HPBTazpIMtk'
chatid='1154009826'

bot=telegram.Bot(token)

def send_to_doctor(cname):
	print('Sending Message to Doctor')
	bot.send_message(chatid,"Emergency Occured at " + cname+", Consult Immediately or call to 9398586686")
	print('Message Sent')