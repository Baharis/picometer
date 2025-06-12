# picometer

[![PyPI version](https://img.shields.io/pypi/v/picometer)](https://pypi.org/project/picometer/)
[![Python version](https://img.shields.io/pypi/pyversions/picometer.svg)](https://www.python.org/downloads/)
[![codecov](https://codecov.io/gh/Baharis/picometer/graph/badge.svg?token=bWGMArFAR8)](https://codecov.io/gh/Baharis/picometer)
[![CodeFactor](https://www.codefactor.io/repository/github/baharis/picometer/badge)](https://www.codefactor.io/repository/github/baharis/picometer)
[![Documentation Status](https://readthedocs.org/projects/picometer/badge/?version=stable)](https://picometer.readthedocs.io/en/stable/?badge=stable)
[![Gitmoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg)](https://gitmoji.dev)
[![tests](https://github.com/Baharis/picometer/actions/workflows/ci-cd.yml/badge.svg?branch=master)](https://github.com/Baharis/picometer/actions/workflows/ci-cd.yml)

Picometer is a Python 3.10+ package which allows to define
and calculate various metrics across multiple crystal structures
in a clear and reproducible fashion.
It is supposed to be used in tandem with a GUI program
such as [Mercury](https://www.ccdc.cam.ac.uk/solutions/software/mercury/)
or [Olex2](https://www.olexsys.org/olex2/)
and applied on a series of cif files with consistent labelling.

This is a software for you if you have ever:
- Misclicked and lost your 250-atom selection,
- Tried to fit or calculate metrics for any plane or line,
- Spent a day measuring distances and angles in tens of similar structures,
- Had to redo measurements because of an offensively minor change,

Instead of relying on a graphical interface, picometer reads settings
and instructions from an input [`.yaml`](https://en.wikipedia.org/wiki/YAML)
file to probe one or many consistently-named structures concurrently.
The results are output in a form
of a [`.csv`](https://en.wikipedia.org/wiki/Comma-separated_values) file,
which can be then opened in a spreadsheet editor for further analysis.
Because of that, picometer is a handy tool to save time
on dumb repeatable labor and focus on what really matters.


## Installation

If you are installing python solely to run picometer or are not concerned
about introducing additional dependencies,
installing picometer is as simple as running:
```commandline
pip install picometer
```

However, it is advised to install picometer in a designated
[virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments).
This is best achieved by following the linked instructions,
but can be otherwise summarised as follows:
1) Make sure you have Python 3.10+ installed:
   `python --version`
2) Create a virtual environment using i.e. venv:
   `python -m venv /path/to/virtual_environment`
3) Activate your virtual environment:
   - Windows: `\path\to\virtual_environment\Scripts\activate`
   - Unix/macOS: `source /path/to/virtual_environment/bin/activate`
4) Install `picometer` and its dependencies: `pip install picometer`


The code is currently updated with an intention to be available for download
directly from pip:
```bash
$ pip install picometer
```


## Usage

Whenever you want to use picometer, first re-activate the virtual environment
created during installation following instructions therein.
Running the program with no arguments produces the help string.

```shell
python -m picometer
```
```text
usage: picometer [-h] filename

Precisely define and measure across multiple crystal structures

positional arguments:
  filename    Path to yaml file with routine settings and instructions

options:
  -h, --help  show this help message and exit

Author: Daniel Tchoń, baharis @ GitHub
```

Picometer inputs its settings and instructions from an input
[`.yaml`](https://en.wikipedia.org/wiki/YAML) file.
The file can contain a dictionary of `settings`,
as well as a list of `instructions`.
The list of instructions, called also a "routine", must include
only single-element maps in the `- instruction: detail`
or `- instruction: {details}` format.
Examples of instruction files are available in the `tests` directory.
The easiest way to generate your file is to prepare it based
on the example provided.


## Instructions

The following instructions are currently supported by picometer:
- **Input/output instructions**
  - `load` model from a cif file, given `filename` or mapping syntax:
    `{path: filename.cif, block: cif_block}`.
  - `write` table with all evaluations to a csv file.
- **Selection instructions**
  - `select` atoms, groups, or shapes to be used; use raw element names
    or provide symmetry relation / recenter using mapping syntax, for example:
    `{label: C(11), symm: x;-y;z+1/2, at: Fe(1)}`.
    By default, selection is cleared after calling `select` with no arguments
    or calling an aggregating or evaluating instruction.
  - `recenter` selection around a new centroid;
      this action is applied to every selected item individually,
      so to recenter fixed group of atoms, `group` them first and recenter
      this group - otherwise you will recenter individual atoms instead.
- **Aggregation instructions**
  - `group` current selection into a new object with fixed elements.
  - fit `centroid` to the current atom / centroid selection;
  - fit `line` to the current atom / centroid selection;
  - fit `plane` to the currect atom / centroid selection;
- **Evaluation instructions**
  - write out fractional `coordinates` of currently selected centroids or atoms.
  - write out `displacement` parameters of currently selected centroids or atoms
    (note: currently does not correctly handle symmetry transformations).
  - measure `distance` between 2 selected objects; if the selection includes
    groups of atoms, measure closes distance to the group of atoms.
  - measure `angle` between 2–3 selected objects: planes, lines, or (ordered) atoms.
  - measure `dihedral` andle between 4 individually-selected ordered centroids/atoms.


## Contributing

Interested in contributing? Check out the
[contributing guidelines](CONTRIBUTING.md).
Please note that this project is released with
a [Code of Conduct](CODE_OF_CONDUCT).
By contributing to this project, you agree to abide by its terms.


## License

`picometer` was created by Daniel Tchoń.
It is licensed under the terms of the [MIT license](LICENSE).


## Credits

This software has been written as a hobby project of Daniel Tchoń
(email: dtchon at lbl dot gov, or other address currectly available on
https://dtools.pl/about/).
All contributions and suggestions are heartily welcome!

`picometer` was created with the help of
[`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/)
and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
It is published with the help of
[`poetry`](https://python-poetry.org/),
[Python Semantic Versioning](https://python-semantic-release.readthedocs.io/en/latest/),
and [Gitmoji](https://gitmoji.dev/).
