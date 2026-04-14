import re

class Message:
    def __init__(self, message) -> None:
        try:
            self.message_id = message["message_id"]
            self.chat_id = message["chat"]["id"]
            self.user_id = message["from"]["id"]
            self.user_name = message["from"]["first_name"]

            _reply_message = message.get("reply_to_message", False)

            if _reply_message:
                self.reply_message = Message(_reply_message)
            else:
                self.reply_message = None

            text = message.get('caption') or message.get('text') or ''

            self.command, self.text = Message._get_command(text)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print(e)
            raise NotImplementedError


    @classmethod
    def _get_command(cls, text):
        """Separa o comando da mensagem.
        retorno:
            command: string ou none
            text: string (possivelmente vazia)
        """
        regex = r'((?P<command>^/\w*)@?\w*)?(?P<text>[\s\S]*)?'
        match = re.match(regex, text)

        command = match.group('command')
        text = match.group('text').strip()

        return (command, text)


    def __str__(self) -> str:
        return f"nova mensagem: {self.message_id}, {self.user_id}, {self.chat_id}, {self.text}, {self.reply_message}"
