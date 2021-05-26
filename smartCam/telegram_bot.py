def sendMessage(msg, chat_id, bot):
    bot.send_message(chat_id=chat_id, text=msg)


def sendImage(photo, chat_id, bot):
    bot.send_photo(photo=open(photo, 'rb'), chat_id=chat_id)
