import csv
import re
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
# nltk.download('wordnet')
# nltk.download('stopwords')
# nltk.download('averaged_perceptron_tagger')

stop_words = set(stopwords.words('english'))
stop_words.add('hello')
stop_words.add('hey')
stop_words.add('hi')
stop_words.add('sir')
stop_words.add('sioux')
stop_words.add('please')
stop_words.add('thank')
stop_words.add('thanks')
stop_words.add('car')
stop_words.add('sorry')
stop_words.add('request')
stop_words.add('yes')
stop_words.add('apologize')


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)

def lemmatize_stemming(text):
    return WordNetLemmatizer().lemmatize(text, get_wordnet_pos(text))

# This code was used to preprocess and clean the English Dictionary raw value
# We acquired from Ubuntu WAmerican package
def PreProcessAndCleanEnglishDictionary():
    with open('english.txt', 'r') as f:
        english_words = f.readlines()
    english_words = set([lemmatize_stemming(
        x.strip().lower().replace('\'s', '')) for x in english_words])
    english_words = [word for word in english_words if word not in stop_words]
    with open('english_processed.txt', 'w') as outfile:
        outfile.write("\n".join(english_words))

def ReadEnglishDictionary():
    with open('english_processed.txt', 'r', encoding='latin1') as f:
        english_words = f.readlines()
    english_words = set([word.strip().lower() for word in english_words])
    english_words = dict.fromkeys(english_words, None)
    return english_words

english_words = ReadEnglishDictionary()
def AddOurReplacements(cleanup_replace_words):
    cleanup_replace_words["vehicle"] = "car"
    cleanup_replace_words["truck"] = "car"
    cleanup_replace_words["bus"] = "car"
    cleanup_replace_words["honda"] = "car"
    cleanup_replace_words["civic"] = "car"
    cleanup_replace_words["impala"] = "car"
    cleanup_replace_words["mazda"] = "car"
    cleanup_replace_words["audi"] = "car"
    cleanup_replace_words["volkswagen"] = "car"
    cleanup_replace_words["pontiac"] = "car"
    cleanup_replace_words["jeep"] = "car"
    cleanup_replace_words["toyota"] = "car"
    cleanup_replace_words["hyundai"] = "car"
    cleanup_replace_words["suzuki"] = "car"
    cleanup_replace_words["chevrolet"] = "car"
    cleanup_replace_words["buick"] = "car"
    cleanup_replace_words["dodge"] = "car"
    cleanup_replace_words["nissan"] = "car"
    cleanup_replace_words["renault"] = "car"
    cleanup_replace_words["mitsubishi"] = "car"
    cleanup_replace_words["oldsmobile"] = "car"
    cleanup_replace_words["mercedes"] = "car"
    cleanup_replace_words["ford"] = "car"
    cleanup_replace_words["automobile"] = "car"
    cleanup_replace_words["tata"] = "car"
    cleanup_replace_words["swift"] = "car"
    cleanup_replace_words["micra"] = "car"
    cleanup_replace_words["corolla"] = "car"
    cleanup_replace_words["tiago"] = "car"
    cleanup_replace_words["taurus"] = "car"
    cleanup_replace_words["crossover"] = "car"
    cleanup_replace_words["cherokee"] = "car"
    cleanup_replace_words["chevy"] = "car"

    cleanup_replace_words["buying"] = "buy"
    cleanup_replace_words["purchase"] = "buy"
    cleanup_replace_words["purchasing"] = "buy"
    cleanup_replace_words["crash"] = "accident"
    cleanup_replace_words["crashed"] = "accident"
    cleanup_replace_words["collision"] = "accident"
    cleanup_replace_words["accident"] = "accident"
    cleanup_replace_words["totaled"] = "accident"
    return cleanup_replace_words

def ReadCleanupText():
    values = {}
    # github.com/pratikpc/AIHackathon/blob/master/spelling-lemmatized.csv
    with open("spelling-lemmatized.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        for line in reader:
            key = line[0].strip().lower()
            value = line[1].strip().lower()
            values[key] = value
    return values
cleanup_replace_words = ReadCleanupText()
cleanup_replace_words = AddOurReplacements(cleanup_replace_words)

def ApplyCleanup(sentence):
  def ReplaceToAmericanEnglishWithoutShortCuts(word):
      if word in cleanup_replace_words:
          word = cleanup_replace_words[word]
      return word

  def IsEnglishWord(word):
      return (word in english_words)
  
  sentence = sentence.strip().lower()
  # Remove Mentions and URLs
  sentence = str(sentence)
  sentence = re.sub(r'\S*@\S*\s?', '', sentence)
  sentence = re.sub(r'https?://\S+', '', sentence)
  sentence = re.sub(
      r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)', '', sentence)
  sentence = re.sub(r"[^A-Za-z]", " ", sentence)
  sentence = re.sub(r"(?:\@|https?\://)\S+", "", sentence)
  split = sentence.split()
  split = [ReplaceToAmericanEnglishWithoutShortCuts(
      lemmatize_stemming(word)) for word in split if len(word) > 2]
  sentence = ' '.join(split)
  split = sentence.split()
  split = [
      word for word in split if word is not None and word not in stop_words and IsEnglishWord(word)]
  if (len(split) < 1):
      return None
  sentence = ' '.join(split)
  return sentence

if __name__ == "__main__":
    PreProcessAndCleanEnglishDictionary()