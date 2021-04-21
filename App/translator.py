import app_utils

from googletrans import Translator

GoogleTranslatorAPIFunc = Translator()
GoogleTranslatorCodes = {
    "English" : "en",
    "Hindi" : "hi",
    "Marathi" : "mr"
}
def TranslateToEnglishUsingGoogle(text, language):
    text = GoogleTranslatorAPIFunc.translate(text, dest='en', src=GoogleTranslatorCodes[language])
    text = text.text
    print("goog")
    return text

import os
app_utils.create_fullpath_if_not_exists("tmp")

# Command to call on command line to start translation
def get_command(language):
    return "python3 ./models/translator/translate.py -model ./models/translator/" + language + ".pt  -src ./tmp/input_translate_" + language + ".txt -output ./tmp/output_translated_" + language + ".txt -replace_unk"

def merged_text(text):
    text = text.split(' ')
    text_res = []
    for i in range(0, len(text),10):
        text_cur = text[i: i+9]
        text_cur = " ".join(text_cur)
        text_res.append(text_cur)
    text_res = "\n".join(text_res)
    return text_res

def TranslateToEnglishUsingSeqModel(text, language):
    # This translates to English
    if (language == "English"):
        return text
    text = merged_text(text)
    with open("tmp/input_translate_"    + language + ".txt", "w") as inner:
        inner.write(text)
    os.system(get_command(language))
    with open("tmp/output_translated_" + language + ".txt", "r") as outer:
        text = outer.readlines()
    text = "".join(text)
    return text

def TranslateToEnglish(text, language, translator="Google"):
    if translator == "Google":
        return TranslateToEnglishUsingGoogle(text, language)
    elif translator == "Seq2Seq":
        return TranslateToEnglishUsingSeqModel(text, language)