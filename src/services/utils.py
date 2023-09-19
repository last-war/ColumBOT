from src.services.conversation import create_conversation

qa = create_conversation()


def process_telegram_data(data: dict) -> dict:
    
    is_text = False
    is_document = False
    is_unknown = False
    
    sender_id = ''
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
            text = message['caption']
            file_id = message['document']['file_id']
            mime_type = message['document']['mime_type']
            is_document = True
            is_unknown = False
    
    return {
        'is_text': is_text,
        'is_document': is_document,
        'is_unknown': is_unknown,
        'sender_id': sender_id,
        'text': text,
        'file_id': file_id,
        'mime_type': mime_type
    }



