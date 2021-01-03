#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham

import sacrebleu
from sacremoses import MosesDetokenizer
import argparse
import sys

from .demutate_corpus import DemutateText
from .predict_inference import PredictText
from .apply_mutations import MutateText


def create_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('bleu',
                                       description="Compute the BLEU Score by our modified metrics")
    else:
        parser = argparse.ArgumentParser('bleu',
                                         description="Compute the BLEU Score by our modified metrics")

    parser.add_argument(
        '--reference', '-r', type=argparse.FileType('r'),
        metavar='PATH',
        help='Path to the reference text'
    )
    parser.add_argument(
        '--predictions', '-p', type=argparse.FileType('r'),
        metavar='PATH',
        help='Path to the predicted text'
    )
    parser.add_argument(
        '--language', '-l', type=str,
        metavar='STRING',
        help='Language of text you wish to demutate'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'),
        metavar='PATH', default=sys.stdout,
        help='Path to output file'
    )
    parser.add_argument(
        '--demutated-reference', '-j', type=argparse.FileType('r'),
        metavar='PATH',
        help="Path to demutated reference file. Use this if you're scoring "
             "a demutated NMT model"
    )
    parser.add_argument(
        '--model', '-m', type=argparse.FileType('r'),
        metavar='PATH',
        help="Model name, if not the same as folder name"
    )
    parser.add_argument(
        '--window', '-w', type=int,
        metavar='VALUE',
        help="Length of the window either side of the central token"
    )
    parser.add_argument(
        '--vocab', '-v', type=argparse.FileType('r'),
        metavar='PATH',
        help="Vocab file name, if not 'vocab'"
    )
    parser.add_argument(
        '--labels', '-t', type=argparse.FileType('r'),
        metavar='PATH',
        help="Label file name, if not 'labels'"
    )
    parser.add_argument(
        '--mask', '-k', type=str, default='<mask>',
        metavar='STRING',
        help='Mask Token (Default: <mask>)'
    )
    parser.add_argument(
        '--skip', '-s', type=bool, default=True,
        metavar='BOOL',
        help="Don't mutate words containing punctuation [default: True]"
    )
    parser.add_argument(
        '--possible-labels', '-c', nargs='+',
        metavar='LIST',
        help="List of the labels used in neural network (USE ONLY IF YOU USE A CUSTOM NETWORK)"
    )


def celtic_bleu(ref, pred, language, mutated_ref=None, data=None, window=None,
                vocab_name=None, label_name=None, model_name=None, mask='<mask>',
                skip=True, output_file=None, possible_labels=None):
    """
    :param ref: Reference Text (If demutated NMT model, this is demutated reference)
    :param pred: Predictions (If demutated NMT model, this is demutated predictions)
    :param language: Language of text
    :param mutated_ref: Mutated Reference Text (Use if demutated NMT model)
    :param data: Path to neural network data folder (with model, vocab and label vocab)
    :param window: Window size (on each side)
    :param vocab_name: Name of vocab file in folder (if not 'vocab')
    :param label_name: Name of label file in folder (if not 'labels')
    :param model_name: Name of model in folder (if not the same as the folder name)
    :param mask: Mask/padding token (Default: <mask>)
    :param skip: Skip words with punctuation (default: True)
    :param output_file: File to output scores
    :param possible_labels: The labels used in your custom neural network
    :return: Standard and Demutated BLEU scores
    """
    demutation = DemutateText(language)
    if not isinstance(ref, list):
        ref = [ref]

    if not isinstance(pred, list):
        pred = [pred]

    if mutated_ref:
        if not isinstance(mutated_ref, list):
            mutated_ref = [mutated_ref]

        if not data:
            raise Exception('Missing data folder when using Demutated NMT evaluation!')

        predictor = PredictText(language, data, window, mask, possible_labels, vocab_name, label_name, model_name)
        predictions = predictor.predict(pred)
        remutate = MutateText(language, skip_with_punc=skip)
        mutated_pred = remutate.mutate_text(predictions)

        md = MosesDetokenizer(lang=language)
        detok_ref = [[md.detokenize(x.split()) for x in ref]]
        detok_pred = [md.detokenize(x.split()) for x in pred]
        detok_mut_ref = [[md.detokenize(x.split()) for x in mutated_ref]]
        detok_mut_pred = [md.detokenize(x.split()) for x in mutated_pred]
        print(detok_ref, detok_pred, detok_mut_ref, detok_mut_pred)

        standard_bleu = sacrebleu.corpus_bleu(detok_mut_pred, detok_mut_ref).score
        demutated_bleu = sacrebleu.corpus_bleu(detok_pred, detok_ref).score

        if output_file:
            with open(output_file, 'w') as out:
                out.write(f'Standard BLEU (With Initial Mutations): {standard_bleu}\n')
                out.write(f'Demutated BLEU (Without Initial Mutations) {demutated_bleu}')
        else:
            return standard_bleu, demutated_bleu

    dem_ref, _ = demutation.demutate_corpus(ref)
    dem_pred, _ = demutation.demutate_corpus(pred)
    md = MosesDetokenizer(lang=language)
    detok_dem_ref = [[md.detokenize(x.split()) for x in dem_ref]]
    detok_dem_pred = [md.detokenize(x.split()) for x in dem_pred]
    detok_ref = [[md.detokenize(x.split()) for x in ref]]
    detok_pred = [md.detokenize(x.split()) for x in pred]

    standard_bleu = sacrebleu.corpus_bleu(detok_pred, detok_ref).score
    demutated_bleu = sacrebleu.corpus_bleu(detok_dem_pred, detok_dem_ref).score

    if output_file:
        if output_file == '<stdout>':
            print(f'Standard BLEU (With Initial Mutations): {standard_bleu}\n'
                  f'Demutated BLEU (Without Initial Mutations) {demutated_bleu}')
        else:
            with open(output_file, 'w') as out:
                out.write(f'Standard BLEU (With Initial Mutations): {standard_bleu}\n')
                out.write(f'Demutated BLEU (Without Initial Mutations) {demutated_bleu}')
    else:
        return standard_bleu, demutated_bleu
