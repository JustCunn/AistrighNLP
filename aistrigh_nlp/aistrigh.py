#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs

from .demutate_corpus import demutate_corpus
from .demutate_corpus import create_parser as get_demutate_corpus_parser

def parse_args():

    args_parse = argparse.ArgumentParser()
    subparsers = args_parse.add_subparsers(dest='command',
                                       help="""Commands""")

    demutate_corpus_parser = get_demutate_corpus_parser(subparsers)
    args = args_parse.parse_args()
    return args

def main():
    args = parse_args()

    if args.command == 'demutate-corpus':
        print(args.input.name)
        if args.input.name != '<stdin>':
            args.input = codecs.open(args.input.name, encoding='utf-8')
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        demutate_corpus(args.input, args.output)
