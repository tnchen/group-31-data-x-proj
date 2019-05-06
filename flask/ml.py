import os
from pathlib import Path
import pickle
import sklearn

# Load the gun violence data
directory = os.path.dirname(os.path.dirname(__file__))


regr = pickle.load(open( os.path.join(directory, 'data', 'rf.pkl'), 'rb' ))
# poly3 = pickle.load(open( os.path.join(directory, 'data', 'poly3.pkl'), 'rb' ))
# lr3 = pickle.load(open( os.path.join(directory, 'data', 'lr3.pkl'), 'rb' ))

def predict(X):
    # trans_X = poly3.transform(X)
    # y = lr3.predict(trans_X)
    y = regr.predict(X)
    if len(y) >= 1:
        y = y[0]
    return y