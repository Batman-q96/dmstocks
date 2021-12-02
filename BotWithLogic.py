from discord_webhook import DiscordWebhook
import GMailApi
import time
from html.parser import HTMLParser

MAX_DISCORD_MESSAGE_LENGTH_IN_CHARS = 2000


class StockBot:
    webhook = DiscordWebhook(
        url='https://discord.com/api/webhooks/810302736226582539/fUWOfh8qSJTzDR1qXUgd2rltP2Z-Fk4d_VtdQC_t9hR7a_1KfYC-9fs_gWMaESo7f33n',
        content="This is a test", username="Magic Stock Bot")

    def send(self):
        content_list = self.webhook.content.split()
        self.webhook.content = content_list[0]
        for content_index in range(len(content_list)):
            if len(self.webhook.content) + len(content_list[content_index]) + 1 < MAX_DISCORD_MESSAGE_LENGTH_IN_CHARS:
                self.webhook.content += " " + content_list[content_index]
            else:
                self.webhook.execute()
                self.webhook.content = content_list[content_index]
        print(self.webhook.content)
        self.webhook.execute()


class MyHTMLParser(HTMLParser):
    text_data = []

    def __init__(self):
        self.text_data = []
        super(MyHTMLParser, self).__init__()

    def handle_data(self, data):
        self.text_data.append(data)


def sanitize_email(email_body):
    if "DOCTYPE html" in email_body:
        parser = MyHTMLParser()
        parser.feed(email_body)
        email_message_string = ""
        for item in parser.text_data:
            if "Alert" in item or "Note" in item or \
                    "ALERT" in item or "NOTE" in item or \
                    "alert" in item or "note" in item:
                email_message_string += item
        return_string = email_message_string.replace('\r', '')
        return_string = return_string.split('~~~')[0]
    else:
        email_message_string = email_body.replace('\r', '')
        return_string = email_message_string.split('\n\n')[0]
    return return_string


if __name__ == '__main__':
    DMStockBot = StockBot()
    dmMailAPI = GMailApi.gmailAPI()
    dmMailAPI.update_messages()
    message_list = dmMailAPI.get_message_bodies(unread_only=False, delete=True)
    for message in message_list:
        message_string = sanitize_email(message.decode("utf-8"))
        print(message_string)
        DMStockBot.webhook.content = message_string
        DMStockBot.send()
        time.sleep(1)
