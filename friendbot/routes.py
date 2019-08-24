from flask import request, jsonify
from friendbot import app, corpus

export = app.config['EXPORT_DIR']
names = corpus.getUserIDs(export)
rev_names = corpus.getUserIDsRev(export)

@app.route('/sentence', methods = ['POST'])
def create_sentence():
    data = request.form
    params = data['text'].split()
    try:
        channel = corpus.interpretChannel(params[0], export)
    except:
        resp = jsonify(text="Error: Channel not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    try:
        userID = corpus.interpretName(params[1], rev_names)
    except:
        resp = jsonify(text="Error: User not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    fulltext = corpus.generateCorpus(export, channel, userID, names)
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    return resp
