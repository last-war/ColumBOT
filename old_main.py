from document_gpt.helper.utils import process_telegram_data, generate_text_response, generate_file_response
from document_gpt.helper.telegram_api import send_message, set_webhook, set_menu_commands


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return 'All is well...'
    elif request.method == 'POST':
        # Обробка POST-запитів тут
        return 'POST request received'

@app.route('/telegram', methods=['POST'])
def telegram_api():
    if request.is_json:
        data = request.get_json()
        print(data)
        try:
            telegram_data = process_telegram_data(data)
            if telegram_data['is_unknown']:
                return 'OK', 200
            if telegram_data['is_text']:
                response = generate_text_response(telegram_data['text'])
                send_message(telegram_data['sender_id'], response)
                return 'OK', 200
            if telegram_data['is_document']:
                response = generate_file_response(
                    telegram_data['file_id'], telegram_data['mime_type'], telegram_data['sender_id'])
                send_message(telegram_data['sender_id'], response)
                return 'OK', 200
        except:
            pass
        return 'OK', 200
        
    
