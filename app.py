from flask import Flask,jsonify,request

def main_function(post):
    import json
    from langdetect import detect_langs
    import spacy
    from collections import Counter
    from string import punctuation
    from nltk.corpus import wordnet
    nlp = spacy.load('en_core_web_lg')
    def get_language(text):
        result = detect_langs(str(text))
        return result

    def get_important_words(text):
        result = []
        pos_tag = ['PROPN', 'ADJ', 'NOUN'] 
        doc = nlp(text.lower()) 
        for token in doc:
            if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
                continue
            if(token.pos_ in pos_tag):
                result.append(token.text)
        output = set(result)
        important = Counter(output).most_common(5)
        return important

    def get_synonyms(word):
        synonyms = []
        for syn in wordnet.synsets(word):
            for i in syn.lemmas():
                synonyms.append(i.name())
        try:
            return synonyms[4]
        except : 
            return word

    language = get_language(post)
    new_lang = str(language).replace('[',"")
    new_lang = str(new_lang).replace(']',"")
    new_lang = new_lang.split(':')
    important_words = get_important_words(post)

    def get_topic(important_words):
        from keytotext import pipeline
        nlp2 = pipeline("k2t-base")
        params = {"do_sample":True, "num_beams":4, "no_repeat_ngram_size":3, "early_stopping":True}
        topic_name = nlp2([important_words[0][0], important_words[1][0], important_words[2][0], important_words[3][0], important_words[4][0]], **params)
        return topic_name

    post_topic = get_topic(important_words)
    dataset = {
        "Language":{"lang_code": new_lang[0], "conf_score":new_lang[1]},
        "Keywords":[
                {"Keyword1":important_words[0][0],"conf_score":important_words[0][1]},
                {"Keyword2":important_words[1][0],"conf_score":important_words[1][1]},
                {"Keyword3":important_words[2][0],"conf_score":important_words[2][1]},
                {"Keyword4":important_words[3][0],"conf_score":important_words[3][1]},
                {"Keyword5":important_words[4][0],"conf_score":important_words[4][1]}
        ],
        "Topic":{ "topic_name":str(post_topic),"conf_score":nlp(str(post_topic)).similarity(nlp(str(post)))},
        "Hashtags" : [
                {"hashtag1" : get_synonyms(str(important_words[0][0])),"conf_score" : nlp(get_synonyms(str(important_words[0][0]))).similarity(nlp(important_words[0][0]))},
                {"hashtag2" : get_synonyms(str(important_words[1][0])),"conf_score" : nlp(get_synonyms(str(important_words[1][0]))).similarity(nlp(important_words[1][0]))},
                {"hashtag3" : get_synonyms(str(important_words[2][0])),"conf_score" : nlp(get_synonyms(str(important_words[2][0]))).similarity(nlp(important_words[2][0]))},
                {"hashtag4" : get_synonyms(str(important_words[3][0])),"conf_score" : nlp(get_synonyms(str(important_words[3][0]))).similarity(nlp(important_words[3][0]))},
                {"hashtag5" : get_synonyms(str(important_words[4][0])),"conf_score" : nlp(get_synonyms(str(important_words[4][0]))).similarity(nlp(important_words[4][0]))}
        ]
    }
    response_data = json.dumps(dataset)
    return response_data


app = Flask(__name__)

@app.route('/api', methods = ['POST','GET'])
def home():
    if(request.method == "GET"):
        return "Can't Handle request on GET method"
    elif (request.method == "POST"):
        post = request.json['user_post']
        data = main_function(post)
        return data
    else :
        return ("Invalid Method for this API")