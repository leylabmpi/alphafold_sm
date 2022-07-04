from __future__ import print_function
import os
import re
import sys
import gzip
import socket
import getpass
try:
    import pandas as pd
except ImportError:
    print('pandas package not found')
    sys.exit(1)

# functions
def J(*args):
    return os.path.join(*args)

def A(path):
    return os.path.abspath(path)

# setup
## load
if len(config.keys()) == 0:
    configfile: 'config.yaml'
## pipeline utils
snake_dir = config['pipeline']['snakemake_folder']
include: snake_dir + 'bin/ll_pipeline_utils/Snakefile'
config_default(config, 'pipeline', 'name')
## output
config['output_dir'] = config['output_dir'].rstrip('/') + '/'
## samples table
config['samples'] = pd.read_csv(config['samples_file'], sep='\t', comment='#')
config['samples']['Sample'].replace('[^a-zA-Z0-9_-]+', '_', regex=True, inplace=True)
config['samples'] = config['samples'].set_index(config['samples'].Sample)
### duplicates?
x = config['samples'].duplicated(subset=['Sample'])
y = config['samples'].loc[x]
if y.shape[0] > 0:
    x = ','.join(y.Sample.tolist())
    ValueError('Sample names are not unique: {}'.format(x))
    
## temp dir
config['pipeline']['username'] = getpass.getuser()
config['pipeline']['email'] = config['pipeline']['username'] + '@tuebingen.mpg.de'
config['tmp_dir'] = os.path.join(config['tmp_dir'], config['pipeline']['username'])
config['tmp_dir'] = os.path.join(config['tmp_dir'], config['pipeline']['name'] + '_' + str(os.stat('.').st_ino) + '/')
sys.stderr.write('\33[33mUsing temporary directory: {} \x1b[0m\n'.format(config['tmp_dir']))

### check: files exist?
for index,row in config['samples'].iterrows():
    file_cols = ['Fasta']
    for f in file_cols:
    	if not os.path.isfile(row[f]):
       	   raise ValueError('Cannot file file: "{}"'.format(row[f]))

# database paths
try:
    data_dir = config['databases']['base_path']
except KeyError:
    raise ValueError('Cannot find "databases: base_path:" parameter in the config')
for k,v in config['databases'].items():
    if k == 'base_path':
        continue
    config['databases'][k] = J(data_dir, v)
       
# Use GPU?
try:
    _ = config['cluster']
except KeyError:
    config['cluster'] = 'False'
if is_true(config['params']['use_gpu']) and not is_true(config['cluster']):
    config['params']['use_gpu'] = 'False'
    sys.stderr.write('\33[33mWARNING: setting use_gpu=False, since the job is local. Use `snakemake --config cluster=True` if actually using a cluster with GPU nodes\x1b[0m')
    
## including modular snakefiles
include: snake_dir + 'bin/dirs'
include: snake_dir + 'bin/alphafold/Snakefile'
include: snake_dir + 'bin/align/Snakefile'

# all rule

def which_all(wildcards):
    F = []
    # predictions
    F += expand(A(af_dir + '{sample}/features.pkl'),
                sample = config['samples'].Sample)
    for i in range(5):
        F += expand(A(af_dir + '{{sample}}/ranked_{}.pdb'.format(i)),
                    sample = config['samples'].Sample)
    # alignents
    ## intra
    if is_true(config['params']['mTM_align']['run_intra']):
        F.append(af_dir + 'mTM-align/intra/scores.tsv')
    ## inter
    if is_true(config['params']['mTM_align']['run_inter']):
        F.append(af_dir + 'mTM-align/inter/scores.tsv')
    # return
    return F

localrules: all
rule all:
    input:
        which_all
