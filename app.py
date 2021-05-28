from flask import Flask, redirect, render_template, request, render_template, session, url_for
from googletrans import Translator
import random
import json
import torch
import bcrypt
from model import NeuralNet
from nltk_utils import *
from dbwork import *

app = Flask(__name__)
app.secret_key = "12ein3riw4ufbi4fo09"
translator = Translator()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


@app.route('/')
def index():
    if "username" in session:
        user = session["username"]
        user = user.split("@")
        user = user[0]
        return redirect(url_for("opt"))
    else:
        return render_template('index.html')


@app.route('/', methods=["POST"])
def indexlogin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")
        print(email, password)
        print("Cpass: ", request.form.get("cpass"))
        if request.form.get("cpass") == None:
            password = bytes(password, 'utf-8')
            details = find(email, password)
            print(details)
            if details != None:
                if bcrypt.checkpw(password, details['password']):
                    print("Logged in successfully..")
                    session["username"] = email
                    return redirect(url_for("opt"))
                else:
                    err = "Incorrect Login Details..."
                    return render_template("index.html", err=err)
            else:
                err = "No account registered with this credentials..."
                return render_template("index.html", err=err)
        else:
            cpass = request.form.get("cpass")
            if password == cpass:
                password = bytes(password, 'utf-8')
                hashed = bcrypt.hashpw(password, bcrypt.gensalt())
                a = insert(email, hashed)
                if a == True:
                    return render_template("index.html")
                else:
                    err = "Error, an account has already been registered on this email ID!"
                    return render_template("index.html", err=err)
            else:
                err = "Error, the passwords don't match!"
                return render_template("index.html", err=err)
    else:
        return render_template("index.html")


@app.route('/opt/')
def opt():
    if "username" in session:
        user = session["username"]
        user = user.split("@")
        user = user[0]
        return render_template('option.html', user=user)
    else:
        return redirect(url_for("index"))


@app.route('/opt/chatbot-mr/')
def index2():
    if "username" in session:
        user = session["username"]
        user = user.split("@")
        user = user[0]
        return render_template('chatbot-mar.html', user=user)
    else:
        return redirect(url_for("index"))


@app.route("/opt/chatbot-mr/get")
def get_bot_response():
    with open('intents.json', 'r', encoding='utf-8') as json_data:
        intents = json.load(json_data)

    FILE = "data.pth"
    data = torch.load(FILE)
    bot_name = "Sam"
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    # get data from input,we write js  to index.html
    userText = request.args.get("msg")
    print(userText)
    sentence = userText
    print("Input statement:", userText)
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                output = random.choice(intent['responses'])
                print(f"{bot_name}: {output}")
    else:
        output = 'मला कळत नाही'
        print(f"{bot_name}: {output}...")

    return output


@app.route('/opt/chatbot-eng/')
def index3():
    if "username" in session:
        user = session["username"]
        user = user.split("@")
        user = user[0]
        return render_template('chatbot-eng.html', user=user)
    else:
        return redirect(url_for("index"))


@app.route("/opt/chatbot-eng/get")
def get_bot_response1():
    with open('intents1.json', 'r') as json_data:
        intents = json.load(json_data)

    FILE = "data1.pth"
    data = torch.load(FILE)
    bot_name = "Sam"
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    # get data from input,we write js  to index.html
    userText = request.args.get("msg")
    sentence = userText
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                output = random.choice(intent['responses'])
                print(f"{bot_name}: {output}")
    else:
        output = "I do not understand"
        print(f"{bot_name}: {output}...")

    return output


@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
