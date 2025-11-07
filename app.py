from flask import Flask
app = Flask(_name_)

@app.route('/')
def home():
    return "Merhaba, Buluttan Selam!"
