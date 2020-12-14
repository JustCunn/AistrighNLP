# AistrighNLP

![Aistrigh](https://github.com/JustCunn/AistrighNLP/blob/master/images/github_aistrigh.png)

AistrighNLP is a collection of tools and models used for Aistrigh, the BT Young Scientist 2021 project. Our aim is to bring Irish into the modern era with NLP tools to give it parity with English.
The tools included are based around the work in [Neural Models for Predicting Celtic Mutations](https://www.aclweb.org/anthology/2020.sltu-1.1.pdf) (Scannell, 2020). Included is all the tools needed to create a demutated Irish corpus, which can be used in all sorts of NLP tasks, and a model to reinsert them. For the Python API docs visit [AistrighNLP Python API](https://github.com/JustCunn/AistrighNLP/blob/master/python.md)

Installing the Package
---------------------------
AistrighNLP can be downloaded using `pip`
```
pip install aistrigh-nlp
```


Lowercasing
---------------------------
When lowercasing either Irish or Scots Gaelic for prediciting mutations, you must be aware of special cases outlined in the paper above. Our lowercaser handles that
```
aistrigh-nlp lowercase -i input.txt -o output.txt
```


Removing mutations
-----------------------
To remove mutations from an entire dataset for use for NLP tasks (like Machine Translation) use `demutate-corpus`
```
aistrigh-nlp demutate-corpus -i input.txt -o output.txt
```

To remove mutations with a 'window' on either side to train a neural network, use `demutate-window`, with `-w` set to your desired window length on each side
```
aistrigh-nlp demutate-window -i input.txt -o output.csv -w 15
```


Predicting the mutations
-------------------------
To predict mutations on each word, use `predict-mutations`. As of right now, it's only compatible with PyTorch+Torchtext/PyTorch models but we are working on expanding to TensorFlow and Keras. You'll need your vocab, labels and model checkpoint. We provide a default model to be used.
```
aistrigh-nlp predict-mutations -i input.txt -o output.txt -w 15 -v my_vocab.pth -l my_labels.pth -m my_model.pt
```


Applying the predicted mutations
-----------------------------------
To apply the mutations predicted by `predict-mutations`, use `apply-mutations`. 
```
aistrigh-nlp apply-mutations -i input.txt -o output.txt -skip
```

`-skip` here means to skip mutating any tokens containing symbols. It's unlikely these tokens need remutating, and will likely hurt performance without this set.


NOTE
--------------------
AistrighNLP uses PyTorch `Traces` to save the full computational graphs as checkpoints. This way, the model architecture need not be declared into hard-coded scripts. See this [StackOverflow Thread](https://stackoverflow.com/questions/59287728/saving-pytorch-model-with-no-access-to-model-class-code) for instructions to save a traced checkpoint.

