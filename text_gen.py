

import tensorflow as tf
print(tf.__version__)
from tensorflow import set_random_seed
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.layers import Embedding, GRU, Dense, Dropout, SpatialDropout1D
from keras.models import Sequential
from keras.callbacks import EarlyStopping, ModelCheckpoint
import pickle

import numpy as np
from numpy.random import seed
import pandas as pd
import re
from random import shuffle
import random

"""We'll be setting up random seeds to reproduce our results."""

seed(1)
set_random_seed(2)
random.seed(3)

"""Since we were using colabs, we need to import our data from our drive."""

"""Let's begin reading the lines."""

lines_df = pd.read_csv('breakdown-2.csv',error_bad_lines= False )
lines_df = lines_df.iloc[:,0]

"""Let us take a look at what we've got."""

print(lines_df.iloc[3])

"""Now let us begin by cleaning the texts.
We'll be removing all punctuation, digits and special characters, keeping only the text and whitespace.


We'll also shuffle our dataset.
"""

def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"how's", "how is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"[^A-Za-z\s]", "", text)
    return text

clean_lines = lines_df.apply(lambda x: clean_text(x))
print(clean_lines[0])
shuffle(clean_lines)
print(clean_lines[0])
print(f"Number of lines are {len(clean_lines)}")

"""Now we'll convert our text in sequences and then using the N-gram model convert it into a sequence of N-words.

An N-gram is a sequence of N words: a 2-gram (or bigram) is a two-word sequence of words like “look over”, “over there” and a 3-gram (or trigram) is a three-word sequence of words like “look over there”.
"""

tokenizer = Tokenizer()

def get_sequence_tokens(text):
    
    tokenizer.fit_on_texts(text)
    total_words = len(tokenizer.word_index) + 1
    
    input_sequences = []
    for line in text:
        token_list = tokenizer.texts_to_sequences([line])[0]
        for i in range(1, len(token_list)):
            n_gram_sequence = token_list[:i+1]
            input_sequences.append(n_gram_sequence)
    return input_sequences, total_words

text_sequences, total_words = get_sequence_tokens(clean_lines[:10])
print(text_sequences[:5])
print(tokenizer.sequences_to_texts(text_sequences[:5]))
print(f"Length of sequences array {len(text_sequences)}")

"""As you can see from the example above, the sentence is converted into N number of words.

Now while feeding data, we require the number of inputs to be constant.

However every sentence will not have the same number of words in it.

Hence, inorder to adjust for this varying length we pad the sentences (pre or post).

The maximum sequence size is defined by the maximum length in the input_sequences.
"""

def generate_padded_sequences(input_sequences):
    max_sequence_length = max([len(x) for x in input_sequences])
    input_sequences = np.array(pad_sequences(input_sequences,
                                             maxlen=max_sequence_length,
                                             padding='pre'))
    
    predictors, label = input_sequences[:,:-1], input_sequences[:,-1]
    
    label = tf.keras.utils.to_categorical(label, num_classes=total_words)
    
    return predictors, label, max_sequence_length

predictors, label, max_sequence_length = generate_padded_sequences(text_sequences)
print(f"Total number of words: {total_words} | Maximum sequence length: {max_sequence_length}")
print(predictors[0])

"""We will now build the model using an Embedding layer and Stacked GRUs each with their own Dropout layer.

The mask_zero in the Embedding layer tells the model to ignore the padded zeros.
"""

def build_model(max_sequence_length, total_words):
    input_len = max_sequence_length - 1
    model = Sequential()
    
    model.add(Embedding(total_words, 128, input_length=input_len, mask_zero=True))
    model.add(SpatialDropout1D(0.5))
    
    model.add(GRU(512, return_sequences=True))
    model.add(Dropout(0.2))
    
    model.add(GRU(512))
    model.add(Dropout(0.1))
    
    model.add(Dense(total_words, activation='softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    return model

model = build_model(max_sequence_length, total_words)
model.summary()

"""To start training, we fit the model to the training data."""

# Training the model
model.fit(predictors, label, batch_size=32, epochs=20)

"""Saving the model to use in the future."""

model.save('model_text_gen.h5')

"""The generate_text method uses a start word or phrase that is used to predict the next probable word. This word is then added to the overall output and is fed to the model again to generate the next word. This keeps on continuing till we reach the desired number of words. 

As our model was trained on sequences of text, we perform the same conversion before every prediction.

In case we provide a word out of the model's vocabulary, we choose a random class from the top 10 classes the model predicts. We do this to avoid the same output sequence for every word not from its vocabulary list.
"""

def generate_text(seed_text, num_words, model, max_sequence_length):
    for _ in range(num_words):
        generate_random = False
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        if len(token_list) == 0:
            generate_random = True
        token_list = pad_sequences([token_list],
                                   maxlen=max_sequence_length - 1,
                                             padding='pre')
        predicted = model.predict_classes(token_list, verbose=0)
        if generate_random:
            pred_list = np.argsort(-model.predict_proba(token_list))[0]
            predicted = pred_list[np.random.randint(low=0, high=10)]
            print(predicted)
        
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break
        seed_text += " " + output_word
    return seed_text.title()

"""Let's generate some text using the function we created above."""

print(generate_text("he said", 15, model, max_sequence_length))

"""Let's load our model as try predicting text using the new_model"""

new_model = tf.keras.models.load_model('model_text_gen.h5')
new_model.summary()

print(generate_text("he said", 15, new_model, max_sequence_length))

"""As you can see from the above output the new_model is exactly the same as the original model.

A few more examples below.
"""

print(generate_text("death", 5, model, max_sequence_length))
print(generate_text("lord", 10, model, max_sequence_length))
print(generate_text("seek", 15, model, max_sequence_length))
print(generate_text("good", 20, model, max_sequence_length))
print(generate_text("silence", 25, model, max_sequence_length))

"""Saving the tokenizer for future use."""

# saving
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)