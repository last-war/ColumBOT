
def process_telegram_data(data: dict) -> dict:
    
    is_text = False
    is_document = False
    is_unknown = False
    
    sender_id = ''
    is_bot = ''
    first_name = ''
    username = ''
    text = ''
    file_id = ''
    mime_type = ''
    if 'message' in data.keys():
        message = data['message']
        sender_id = message['from']['id']
        if 'text' in message.keys():
            text = message['text']
            is_text = True
            is_unknown = False
        if 'document' in message.keys():
            if 'caption' in message.keys():
                text = message['caption']
            file_id = message['document']['file_id']
            mime_type = message['document']['mime_type']
            is_document = True
            is_unknown = False
        if 'from' in message.keys():
            is_bot = message['from']['is_bot']
            first_name = message['from']['first_name']
            username = message['from']['username']

    return {
        'is_text': is_text,
        'is_document': is_document,
        'is_unknown': is_unknown,
        'sender_id': sender_id,
        'is_bot': is_bot,
        'first_name': first_name,
        'username': username,
        'text': text,
        'file_id': file_id,
        'mime_type': mime_type
    }



