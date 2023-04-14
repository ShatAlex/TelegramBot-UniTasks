async def echo_send(message):
    await message.answer('Неизвестная команда -_-')


def register_handlers_other(dispatcher):
    dispatcher.register_message_handler(echo_send)
