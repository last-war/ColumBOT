# ColumBOT
 GoIT DataScience team5 - BOT name @ai_Colum_bot
 
- reg your bot on BotFather insert TELEGRAM_TOKEN in ENV file
- insert your BASE_URL `https://api.telegram.org/bot{TELEGRAM_TOKEN}` in ENV file
- install requirements.txt
- run docker `docker run --name columbot -p 5432:5432 -e POSTGRES_PASSWORD=secret -d postgres -e ` where secret- your pass
- use DBeaver to create db
- insert DATABASE_URL in ENV file like `postgresql+psycopg2://postgres:secret@localhost:5432/columbotdb` where secret- your pass
- run alembic / generate magration `alembic upgrade head`
- start app `uvicorn main:app --host localhost --port 8000 --reload`
- reg on `huggingface.co` and from `https://huggingface.co/settings/tokens` in ENV file _HF_API_KEY
- install for https webhook telegram linux ->`snap install ngrok` if win or mac -> off documentation
- add key ngrok `ngrok config add-authtoken <key>`
- start ngrok `ngrok http 8000` and find `<ngrok url>` it look like `https://XXXX-XXX-XXX-XXX-XXX.ngrok-free.app`
- activate webhook open `"<ngrok url>/docs#/telegram/set_telegram_webhook_api_telegram_set_telegram_webhook_post`
send:
`{
  "ngrok_url": "<ngrok url>/api/telegram/bot",
  "secret_token": "<GUID secret token>"
}
`
GUID secret token come up with it yourself according to the rules in the documentation. will work with this too.
  sample `1111111-111111-aaaaaaasaaA-XxXxXxXxXxXxXxXxXx`
- create menu in bot execute -> `<ngrok url>/api/settings`


## Install and run from docker-compose

Create .env file from example_env.txt
run `cd docker_publication`
run `chmod +x run_presets.sh`
run `./run_presets.sh`

And then see the instructions from above. ngrok ........- >

