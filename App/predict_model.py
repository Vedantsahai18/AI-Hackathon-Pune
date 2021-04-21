from cleanup import ApplyCleanup
from sklearn.feature_extraction.text import CountVectorizer

import ktrain
import numpy as np
import app_utils

# Initially None
# Initialised by Other Thread
reloaded_predictor = None

def load_model():
    print("Start BERT Model loading")
    global reloaded_predictor
    reloaded_predictor = ktrain.load_predictor('models/predictor3_83')
    text = "want buy"
    reload_preds = reloaded_predictor.predict([text], return_proba=True)
    print("Done BERT Model loading")

# load_model()
import threading

# Using Threads to ensure that Loading of Model is carried out in Parallel
ModelColdStarter = threading.Thread(name="Model Cold Start", target=load_model)
ModelColdStarter.start()

target_names = ['New Car Enquiry','Test Drive Enquiry',
                'Breakdown', 'Feedback', 'Vehicle Quality']

def PredictResults(text):
    text = ApplyCleanup(text)
    if text is None or len(text) == 0:
        text = "my car broke down"
    app_utils.DebugCommand("Cleaned Results: ", text)
    reload_preds = reloaded_predictor.predict([text], return_proba=True)
    app_utils.DebugCommand(reload_preds)
    reload_preds = [np.argmax(x) for x in reload_preds]
    return [target_names[pred] for pred in reload_preds]