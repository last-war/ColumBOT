# ColumBOT
 GoIT DataScience team5

- install for https webhook telegram linux ->`snap install ngrok` if win or mac -> off documentation
- add key ngrok `ngrok config add-authtoken <key>`
- start ngrok `ngrok http 8000`
- start app `uvicorn main:app --host localhost --port 8000 --reload`
- activate webhook in postman send post request

   `{
    "url": "<ngrok url>/api/telegram/bot",
    "secret_token": "62s8d56-255d51-AAFata4sbLba-PDTUy9Qr4qGUU-hjX5xMu6qZwY5b4LE"
    }`

    secret token come up with it yourself according to the rules in the documentation according to the type as in the sample. will work with this too.

- create menu in bot execute -> `<ngrok url>/api/settings`