from src.services.conversation import create_conversation

qa = create_conversation()


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
        'mine_type': mime_type,
    }


def generate_text_response(text: str) -> str:
    
    if text == '/start':
        return "Hi, I can help you with saving you data to the clod and retive it, I can also help you with your questions."
    if text == '/file':
        return "Selected PDF document file that you want to query."
    if text == '/help':
        return "I am an AI and I am here to help you. You can upload PDF files and once uploaded, you can query them."
    
    '''TODO
    we can add chat history here...
    save all message in a DB
    retrieve when this function called
    create chat history variable and pass it in the qa
    '''
    
    result = qa(
        {
            'question': text,
            'chat_history': {}
        }
    )
     
    try:
        return result['answers']
    except:
        return 'We are facing some technical issue.'

