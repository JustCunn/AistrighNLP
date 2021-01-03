Python API
==========================

Lowercase
-----------------------

```python
import aistrigh_nlp.utils as utils

text = 'Cá bhfuil ár nAthar?'

lowercased_text = utils.lowercase(text)  # cá bhfuil ár n-athar?
```


Removing mutations
--------------------
```python
from aistrigh_nlp.demutate_corpus import DemutateText

# Create a demutated dataset for NLP tasks

text = ['cá bhfuil a mhála ?', 'tá sé ar an mbord']

demutate = DemutateText(language='ga')

demutated_text, labels = demutate.demutate_corpus(text)

########################################################
#>>> corpus = ['cá fuil a mála ?', 'tá se ar an bord'] #
#                                                      #
#>>> labels = [['none', 'uru', 'none', 'seimhiu'],     #
#              ['none', 'none', 'none', 'none', 'uru'] #
#                                                      #
########################################################


# Create a demutated dataset with a window to train a neural network

import aistrigh_nlp.demutate_window as window

text = 'cá bhfuil a mhála ?'

df = window.demutate_with_window(text, win_len=16, language='ga')  # Returns a Pandas DF object
```


Predicting mutations
------------------------
```python
from aistrigh_nlp.predict_inference import PredictText

text = 'conaic mé madra sa clós'
data = 'path/to/data' # Neural Network data folder

predict = PredictText(language='ga', data_path=data, win_len=16)

predictions = predict.predict(text)
```

`predictions` will be in a unusual form, like 
```
conaic<<SEP>>mé<<SEP>>madra<<SEP>>sa<<SEP>>clós<<SEP>>5<<SEP>>seimhiu<<SEP>>none<<SEP>>none<<SEP>>none<<SEP>>seimhiu<<SEP>>
```
The number in the middle is the length of the sequence. The tokens to the right are the labels of each word. `<<SEP>>` is used to separate each token.


Applying Mutations
------------------------
```python
from aistrigh_nlp.apply_mutations import MutateText

mutate = MutateText(language='ga')

mutated_text = mutate.mutate_text(predicitons)
```


Scoring Celtic NMT models using our Modified Metric (Standard+Demutated BLEU)
-------------------------------------------------------------------------------
```python
from aistrigh_nlp.bleu import celtic_bleu
# If you have a mutated reference and predictions (Standard NMT model)
ref = ["""Ref Text"""]
preds = ["""Pred Text"""]

standard_bleu, demutated_bleu = celtic_bleu(ref=ref, pred=preds, language='ga')
```
```python
# If you have a demutated+original reference and demutated reference
# (i.e. used a demutated NMT model), you'll need to remutate your predictions using our neural networks
from aistrigh_nlp.bleu import celtic_bleu

dem_ref = ["""Demutated Ref Text"""]
dem_preds = ["""Demutated Pred Text"""]
orig_ref = ["Origianl Ref Text"]
data = '/path/to/data'

standard_bleu, demutated_bleu = celtic_bleu(dem_ref, dem_preds, 'ga', mutated_ref=orig_ref, data=data, 
                                            window=16)
```
