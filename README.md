# picometer

This is a little Python 3.10+ suite which aims to precisely define
and calculate measurements across multiple crystal structures.
This is a software for you if you have ever:
- Misclicked an atom and lost your 250-atom selection in Olex2,
- Tried to fit or calculate distances to a line in Mercury,
- Spent a day measuring distances and angles in tens of similar structures,
- Had to redo measurements because of a offensively minor change,

Instead of relying on a graphical interface and evaluating a single structure
at a time, picometer uses an input yaml file with individual settings
and consecutive instructions to probe multiple structures concurrently.
The results are output in a form of a csv file,
which can be then opened in a spreadsheet editor for further analysis.
Because of that, picometer is a handy tool to save time
on dumb repeatable labor and focus on what really matters.


## Installation

In order to use picometer:
1) Clone (download) the git repository to your computer;
2) Make sure you have Python version 3.10+ installed;
3) Create a virtual environment using i.e. venv:
   `python -m venv /path/to/virtual_environment`
4) Activate your virtual environment:
   use `/path/to/virtual_environment` on Windows or
   `source /path/to/virtual_environment` on Linux/MacOS;
5) Install required python packages: `pip install -r requirements.txt`
6) Test your installation by running `python -m unittest`

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
python picometer.py
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

In order to know what to do, picometer requires an input file
with (settings and) instructions. This file should follow yaml format
and the list of instructions, called "routine", must include
only single-element maps in the `instruction: details` format.
An example of instruction file is available in `tests` directory.
The easiest way to generate your file is to manually write it based
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
  - measure `distance` between 2 selected objects; if the selection includes
    groups of atoms, measure closes distance to the group of atoms.
  - measure `angle` between 2–6 selected objects; if the selection includes
    (ordered) atoms, calculate direct or dihedral angle between presumed bonds.


## Contributing

Interested in contributing? Check out the contributing guidelines.
Please note that this project is released with a Code of Conduct.
By contributing to this project, you agree to abide by its terms.


## License

`picometer` was created by Daniel Tchoń.
It is licensed under the terms of the MIT license.


## Credits

This software has been written as a hobby project of Daniel Tchoń
(email: dtchon at lbl dot gov, or other address currectly available on
https://dtools.pl/about/).
All contributions and suggestions are heartily welcome!

`picometer` was created with the help of
[`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/)
and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
It is published with the help of [`poetry`](https://python-poetry.org/).
