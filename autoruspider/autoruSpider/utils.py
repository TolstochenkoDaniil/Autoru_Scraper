import logging
import telebot

class TelegramHandler(logging.StreamHandler):
    '''
        Requires keyword arguments `token` and `chat_id`
    '''
    def __init__(self, token=None, chat_id=None):
        logging.StreamHandler.__init__(self)
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        
    def emit(self, record):
        msg = record.getMessage()
        
        for chat in self.chat_id:
            self.bot.send_message(chat, msg)