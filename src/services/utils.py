
def process_telegram_data(data: dict) -> dict:
    
    is_text = False
    is_document = False
    is_data = False
    is_unknown = False
    
    sender_id = ''
    is_bot = ''
    first_name = ''
    username = ''
    text = ''
    file_id = ''
    mime_type = ''
    data_ = ''

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
            if 'file_name' in message['document'].keys():
                text = message['document']['file_name']
            file_id = message['document']['file_id']
            mime_type = message['document']['mime_type']
            is_document = True
            is_unknown = False
            if 'caption' in message.keys():
                if 'diagram' in message['caption']:
                    is_document = False
                    is_unknown = False
                    is_text = False
                    text = ''
                    file_id = ''
                    mime_type = ''

        if 'from' in message.keys():
            is_bot = message['from']['is_bot']
            first_name = message['from']['first_name']
            if 'username' in message['from'].keys():
                username = message['from']['username']

    if "callback_query" in data.keys():
        data_ = data['callback_query']
        sender_id = data['callback_query']['from']['id']
        if "data" in data_:
            data_ = data_['data']
            is_data = True

    return {
        'is_text': is_text,
        'is_document': is_document,
        'is_unknown': is_unknown,
        'is_data': is_data,
        'sender_id': sender_id,
        'is_bot': is_bot,
        'first_name': first_name,
        'username': username,
        'text': text,
        'file_id': file_id,
        'mime_type': mime_type,
        'data': data_
    }



