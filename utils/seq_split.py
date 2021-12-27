#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import re
import gzip
import bz2
import argparse
import logging

# logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

# argparse
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass

desc = 'Split multi-seq fasta into per-seq fasta files'
epi = """DESCRIPTION:
A tab-delim table of all sequences is written to STDOUT.
The table maps the sequence ID to the per-seq fasta file.

The --index param can be used to write out just some of the
sequences in the fasta file. This can be useful for batching.
"""
parser = argparse.ArgumentParser(description=desc, epilog=epi,
                                 formatter_class=CustomFormatter)
parser.add_argument('fasta_file', type=str,
                    help='Input multi-seq fasta file')
parser.add_argument('-o', '--outdir', type=str, default='fasta_split',
                    help='Output directory')
parser.add_argument('-i', '--index', type=str, default='0',
                    help='Which sequences to write (eg., 1-10 or 3,5,10)? If "0", all written')
parser.add_argument('--version', action='version', version='0.0.1')

# functions
def _open(infile, mode='rb'):
    """
    Openning of input, regardless of compression
    """
    if infile.endswith('.bz2'):
        return bz2.open(infile, mode)
    elif infile.endswith('.gz'):
        return gzip.open(infile, mode)
    else:
        return open(infile)

def _decode(x):
    """
    Decoding input, if needed
    """
    try:
        x = x.decode('utf-8')
    except AttributeError:
        pass
    return x

def parse_index(idx):
    """
    Parsing user-provided index (which seqs to write)
    """
    if idx == '0':
        return None
    x = idx.split('-')
    if len(x) > 1:
        return set([x for x in range(int(x[0]), int(x[1])+1)])
    return set([int(x) for x in idx.split(',')])

def write_seq(seq_id, header, seq, args, file_list, seq_cnt, idx):
    """
    Writing sequence
    """
    # skip if not in index
    if idx is not None:
        if not seq_cnt in idx:
            return None
    # saving ID => out_file
    outfile = os.path.join(args.outdir,
                           str(len(file_list.keys()) + 1) + '.fasta')
    try:
        _ = file_list[seq_id]
        raise ValueError('Duplicate seq-ID: {}'.format(seq_id[1]))
    except KeyError:
        file_list[seq_id] = os.path.abspath(outfile)
    # writing output
    with open(outfile, 'w') as outF:
        outF.write(header + '\n')
        outF.write(seq + '\n')
    logging.info('File written: {}'.format(outfile))

## main interface function
def main(args):
    """
    Load fasta
    For each seq:
      Write seq as separate fasta
    """
    # output
    os.makedirs(args.outdir, exist_ok=True)
    # index
    idx = parse_index(args.index)
    # parsing
    regex1 = re.compile(r'\t')
    regex2 = re.compile(r'[^A-Za-z0-9_]')
    seq_id = (None,None)
    header = None
    seq = ''
    file_list = {}
    seq_cnt = 0
    with _open(args.fasta_file) as inF:
        for line in inF:
            line = _decode(line).rstrip()
            if line.startswith('>'):
                if seq_id[0] is not None:
                    write_seq(seq_id, header, seq, args, file_list, seq_cnt, idx)
                seq_cnt += 1
                seq_id = (regex1.sub('_', line.lstrip('>')),
                          regex2.sub('_', line.lstrip('>')).rstrip('_'))
                header = line
                seq = ''
            else:
                seq += line
        write_seq(seq_id, header, seq, args, file_list, seq_cnt, idx)
    # writing table
    print('\t'.join(['Sample', 'Fasta', 'SeqID']))
    for k,v in file_list.items():
        print('\t'.join([str(k[1]), v, str(k[0])]))

## script interface
if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
