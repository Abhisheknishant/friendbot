from friendbot import app, corpus
import requests
import flask
import json

export = app.config["EXPORT"]
channel_dict = app.config["CHANNEL_DICT"]
channels = app.config["CHANNELS"]
user_dict = app.config["USER_DICT"]
users = app.config["USERS"]


@app.route("/action", methods=["POST"])
def take_action():
    data = flask.request.form["payload"]
    json_data = json.loads(data)
    button_value = json_data["actions"][0]["value"]
    button_text = json_data["actions"][0]["text"]["text"]
    response_url = json_data["response_url"]
    if button_text == "Send":
        payload = actionSend(button_value)
    elif button_text == "Shuffle":
        payload = errorMessage()
    elif button_text == "Cancel":
        payload = actionCancel()
    else:
        payload = errorMessage()
    requests.post(response_url, data=payload)
    msg = "/action Button: {}"
    format_msg = msg.format(button_value)
    app.logger.info(format_msg)
    return ("", 200)


@app.route("/sentence", methods=["POST"])
def create_sentence():
    params = flask.request.form["text"].split()
    channel = "None"
    user = "None"
    for param in params:
        try:
            channel = corpus.parseArg(param, channels)
        except Exception:
            try:
                user = corpus.parseArg(param, users)
            except Exception as ex:
                return errorResponse(ex)
    fulltext = corpus.generateCorpus(export, channel, user, channel_dict, user_dict)
    num_lines = len(fulltext.splitlines(True))
    sentence = corpus.generateSentence(fulltext)
    resp = createPrompt(sentence, user, channel)
    error = "False"
    resp.headers["Friendbot-Error"] = error
    resp.headers["Friendbot-Corpus-Lines"] = num_lines
    resp.headers["Friendbot-User"] = user
    resp.headers["Friendbot-Channel"] = channel
    msg = "/sentence Channel: {} User: {} Error: {} Lines: {}"
    format_msg = msg.format(channel, user, error, num_lines)
    app.logger.info(format_msg)
    return resp


def errorResponse(ex):
    message = str(ex)
    app.logger.error(message)
    resp = flask.jsonify(text=message)
    resp.headers["Friendbot-Error"] = "True"
    return resp


def errorMessage():
    payload = {
        "response_type": "ephemeral",
        "replace_original": False,
        "text": "Sorry, that didn't work. Please try again.",
    }
    return json.dumps(payload)


def actionCancel():
    payload = {"delete_original": True}
    return json.dumps(payload)


def actionSend(sentence):
    payload = {"response_type": "in_channel", "delete_original": True, "text": sentence}
    return json.dumps(payload)


def createPrompt(sentence, user, channel):
    resp_data = {
        "response_type": "ephemeral",
        "blocks": [
            {"type": "section", "text": {"type": "plain_text", "text": sentence}},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "emoji": True, "text": "Send"},
                        "style": "primary",
                        "value": sentence,
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Shuffle",
                        },
                        "value": "{} {}".format(user, channel),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "emoji": True, "text": "Cancel"},
                        "style": "danger",
                        "value": "cancel",
                    },
                ],
            },
        ],
    }
    return flask.jsonify(resp_data)
