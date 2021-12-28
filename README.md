alphafold_sm
============

Simple snakemake pipeline for each scaling of
[AlphaFold2](https://github.com/deepmind/alphafold)

* Version: 0.1.0
* Authors:
  * Nick Youngblut <nyoungb2@gmail.com>
* Maintainers:
  * Nick Youngblut <nyoungb2@gmail.com>

# Summary

This snakemake pipeline handles the software install and cluster job submission/tracking.

For failed cluster jobs, job resources are automatically escalated in an attempt
to successfully complete the job, assuming that the job died due to a lack of cluster resources (eg., a lack of memory).

Alphafold is run as 2 parts:

* Generation of the MSAs
  * Just CPUs required for database searching
  * All subprocesses will use the same number of CPUs
    * Unlike with the original alphafold code
* Prediction of protein structures
  * GPU usage recommended

To do this, the pipeline utilizes a
[modified version of alphafold](https://github.com/nick-youngblut/alphafold).
Only the user interface has been edited, and not how alphafold actually functions.

### Dependencies 

The setup is based upon the [alphafold_non_docker](https://github.com/kalininalab/alphafold_non_docker).

### Databases

**NOTE:** You may to change the location all of required databases if you do not
have access to the 

# Setup

Clone the pipeline

```
git clone --recurse-submodules <alphafold_sm>
```

If you forgot to use `--recurse-submodules`:

```
cd ./alphafold_sm/bin/
git submodule add https://github.com/leylabmpi/ll_pipeline_utils.git
git submodule add https://github.com/nick-youngblut/alphafold.git
git submodule update --remote --init --recursive
```

Download chemical properties to the common folder

```
wget -q -P bin/scripts/alphafold/alphafold/common/ https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt
```

# Usage

## Conda

You need a conda environment with [snakemake](https://snakemake.readthedocs.io/en/stable/) installed.

Be sure to activate you snakemake conda environment!

## Input

### Databases

You may need to download the required alphafold databases if you do not have access to the database files listed on the `config.yaml`.

### Input Fasta

The pipeline processes each user-provided fasta separately, in parallel.

If running `model_preset: monomer`, then each fasta should contain 1 sequence.
If running `model_preset: multimer`, then each fasta can contain >=1 sequence.

You can use `./utils/seq_split.py` for splitting a multi-fasta into
per-sequence fasta files for input to this pipeline.

### `config.yaml`

The `config.yaml` file sets the parameters for the pipeline.

#### Important parameters

* `use_gpu:`
  * Only used if `cluster=True`, which is set automatically via using `./snakemake_sge.sh` for running the pipeline on the MPI Bio. cluster.
  * If `cluster=False` (eg., if a run on a local server) then only CPUs will be used.
* Other params
  * See the alphafold documentation
* `databases:`
  * `base_path:`
    * All databases are assumed to be within this path
    * In other words, the `base_path` is prepended to all database paths
* `pipeline:`
  * `export_conda:`
    * Export all conda envs at the end of a success run

## WARNINGs

* If you delete the `./snakemake/conda/` directory, then BE SURE TO delete the
`pip_update.done` and `patch.done` files in the output directory, or you have to apply the pip update & patch manually to the alphafold conda environment that snakemake will automatically generate.

## Output

See [the alphafold docs](https://github.com/deepmind/alphafold#alphafold-output)

# TODO

* add seq length calc & resource adjustment

## tools to add
* Structure-based calculations
  * https://github.com/harmslab/pdbtools
  * https://ssbio.readthedocs.io/en/latest/protein.html
  * https://www.biotite-python.org/tutorial/target/index.html#going-3d-the-structure-subpackage
* structural comparison
  * TM-Align
  * [mTM-Align](http://yanglab.nankai.edu.cn/mTM-align)
  * [madoka](http://madoka.denglab.org/)
  * [FATCAT](https://ssbio.readthedocs.io/en/latest/notebooks/FATCAT%20-%20Structure%20Similarity.html)
  * [bio3d](http://thegrantlab.org/bio3d/articles/online/pdb_vignette/Bio3D_pdb.html)
* visualization
  * [ipymol](https://github.com/cxhernandez/ipymol)
