#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs

from .demutate_corpus import demutate_corpus
from .demutate_window import demutate_with_window
from .apply_mutations import MutateText
from .predict_inference import predict
from .utils import lowercase

from .demutate_corpus import create_parser as get_demutate_corpus_parser
from .demutate_window import create_parser as get_window_parser
from .apply_mutations import create_parser as get_apply_parser
from .predict_inference import create_parser as get_inference_parser
from .utils import lowercase_parser as get_lowercase_parser

def parse_args():

    args_parse = argparse.ArgumentParser()
    subparsers = args_parse.add_subparsers(dest='command',
                                       help="""Commands""")

    demutate_corpus_parser = get_demutate_corpus_parser(subparsers)
    window_parser = get_window_parser(subparsers)
    apply_parser = get_apply_parser(subparsers)
    inference_parser = get_inference_parser(subparsers)
    lowercase_parser = get_lowercase_parser(subparsers)
    args = args_parse.parse_args()
    return args

def main():
    args = parse_args()

    if args.command == 'demutate-corpus':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        demutate_corpus(args.input, args.output)

    elif args.command == 'demutate-window':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        demutate_with_window(args.input, args.window_length, args.output, args.mask)

    elif args.command == 'apply-mutations':
        args.input = open(args.input.name, encoding='utf-8').readlines()
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        mutated = MutateText(skip_with_punc=args.skip)
        #text = mutated.process_text(args.input)

        out = mutated.mutate_text(args.input, args.skip)
        for line in out:
            args.output.write(line+'\n')

    elif args.command == 'predict-mutations':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        predict(args.model.name, args.input, args.window, args.vocab.name, args.labels.name, args.mask, args.output)

    elif args.command == 'lowercase':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()

        text = lowercase(args.input)
        with open(args.output.name, 'w') as out:
            for line in text:
                out.write(line + '\n')
