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
import aistrigh.demutate_corpus as corpus

# Create a demutated dataset for NLP tasks

text = ['cá bhfuil a mhála ?', 'tá sé ar an mbord']

corpus, labels = corpus.demutate_corpus(text)

########################################################
#>>> corpus = ['cá fuil a mála ?', 'tá se ar an bord'] #
#                                                      #
#>>> labels = [['none', 'uru', 'none', 'seimhiu'],     #
#              ['none', 'none', 'none', 'none', 'uru'] #
#                                                      #
########################################################


# Create a demutated dataset with a window to train a neural network

import aistrigh.demutate_window as window

text = 'cá bhfuil a mhála ?'

df = window.demuatte_with_window(text, win_len=15)  # Returns a Pandas DF object
```


Predicting mutations
------------------------
```python
import aistrigh_nlp.predict_inference as predict

text = 'conaic mé madra sa clós'
model = 'path/to/model' # A PyTorch checkpoint
vocab = 'path/to/vocab' # A Torchtext vocab object
labels = 'path/to/label'  # A Torchtext vocab object

predictions = predict.predict(model=model, input_file=text, win_len=15, vocab_file=vocab,\
                              label_file=labels, mask='<MASK>')
```

`predictions` will be in a unusual form, like 
```
conaic<<SEP>>mé<<SEP>>madra<<SEP>>sa<<SEP>>clós<<SEP>>5<<SEP>>seimhiu<<SEP>>none<<SEP>>none<<SEP>>none<<SEP>>seimhiu<<SEP>>
```
The number in the middle is the length of the sequence. The tokens to the right are the labels of each word. `<<SEP>>` is used to separate each token.
