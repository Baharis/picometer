# CHANGELOG


## v0.4.0 (2025-06-19)

### :bug:

- :bug: Explicitly assert that length of displacement selection is > 0
  ([`d7bf38c`](https://github.com/Baharis/picometer/commit/d7bf38c5d974ffa0df6e290aae4ba82743e085cd))

- :bug: Fix incorrect labelling when creating new U matrix
  ([`9bd7a79`](https://github.com/Baharis/picometer/commit/9bd7a796ce3045b939333595f8c0b2d48b76b71b))

- :bug: Remove a print remaining after debugging
  ([`ffc1992`](https://github.com/Baharis/picometer/commit/ffc1992a1115b0ae221acdbec0e7a31fb2a88f21))

### :sparkles:

- :sparkles: Correctly transform the U matrix when applying transformation with off-diagonal matrix
  elements
  ([`265736a`](https://github.com/Baharis/picometer/commit/265736a6caac902dd51a69ef1f143770314c16b0))

- :sparkles: introduce `settings.complete_uiso_from_umatrix`
  ([`f18ff36`](https://github.com/Baharis/picometer/commit/f18ff361fb5e2b76aae9a87fe27bbea3b34bfa82))

- :sparkles: introduce `settings.complete_umatrix_from_uiso`
  ([`09f760e`](https://github.com/Baharis/picometer/commit/09f760eb3cb65edaf3fa30754a8fb8ee81a9f133))

### Other

- :white_check_mark: Add a file `cobalt.cif` for testing
  ([`6faaae9`](https://github.com/Baharis/picometer/commit/6faaae9bae4d21aec2ecb69990a0ead6f2effbe3))

- :white_check_mark: Add tests for `complete_uiso_from_umatrix` and `complete_umatrix_from_uiso`
  settings
  ([`de820c7`](https://github.com/Baharis/picometer/commit/de820c785dcd7e5cac2e34ab4018767fcf01e410))

- :white_check_mark: Make atoms spherical in ferrocene2.cif test
  ([`696e727`](https://github.com/Baharis/picometer/commit/696e72745fb10dd51fcab45c1b989b70e0fc43ad))

- :white_check_mark: Test newly-implemented u-matrix transformation
  ([`6703b9b`](https://github.com/Baharis/picometer/commit/6703b9b1e9ec835c2120e6e4776dfd1e67e69ab8))

- 🔀 Merge pull request #8 from Baharis/development
  ([`46e7bd2`](https://github.com/Baharis/picometer/commit/46e7bd2c3209af7d1cdec64a6287316c84b6d0db))

✨ Correctly transform the U matrix when applying transformations


## v0.3.1 (2025-06-18)

### :bug:

- :bug: Allow reading ADPs if they are present only for some of the atoms
  ([`bf29368`](https://github.com/Baharis/picometer/commit/bf2936864ebb7849d3b5bce3f711e3678b76c691))

### Other

- :white_check_mark: Reading from cif should work even if not all atoms are in `aniso` table
  ([`17ec964`](https://github.com/Baharis/picometer/commit/17ec964f9ed0ab3d0fc410909611bbb43487f1a9))

- 🔀 Merge pull request #7 from Baharis/development
  ([`f767f71`](https://github.com/Baharis/picometer/commit/f767f716384d95452b0b2fc6bf9b931f4e6bebb7))

:bug: Allow reading ADPs if they are present only for some of the atoms


## v0.3.0 (2025-06-12)

### :bug:

- :bug: Fix changed hikari interface `SymmOp` became `Operation` in v 0.3.2
  ([`152d0ee`](https://github.com/Baharis/picometer/commit/152d0ee64976ba23263f676f4f58596a56990202))

### :memo:

- :memo: Add short README documentation for newly-added `coordinates` and `displacement`
  ([`d3d3a66`](https://github.com/Baharis/picometer/commit/d3d3a660c3ea77e97deb820fe505dfa9d107f888))

### :sparkles:

- :sparkles: Add instruction `coordinates` which yields selection's fractional coords
  ([`a476ce5`](https://github.com/Baharis/picometer/commit/a476ce5cb3922de9f3be9e3305fee6a64ae08989))

- :sparkles: Add instruction `displacement` which yields selection's Uiso and U** (1/2/3)
  ([`04624c8`](https://github.com/Baharis/picometer/commit/04624c8002bb44e98a6a3f361b4eb03a5d49c009))

- :sparkles: Add simple displacement readout (does not handle symmetry transformations)
  ([`eb48098`](https://github.com/Baharis/picometer/commit/eb48098d3852f82583b37952723b33655d462d7c))

### Other

- :construction_worker: Set `tool.semantic_release.major_on_zero` to avoid accidental release of
  1.0.0
  ([`e2c4db3`](https://github.com/Baharis/picometer/commit/e2c4db33e95ba6dedbcb379fc6e76c98e3cb18f7))

- :test_tube: Add a failing test for overwritten coordinates in table to do in future
  ([`fbddce6`](https://github.com/Baharis/picometer/commit/fbddce6da9d19d17cc8b62c89376d327e588c09d))

- :white_check_mark: Add `displacement` test, modify the `ferrocene1.cif` to have simple Uisos
  ([`521c555`](https://github.com/Baharis/picometer/commit/521c555e0cf3f459a8e2616fcbee0f9b0a42df5d))

- :white_check_mark: Fix broken `test_transformed_group` test which now looks only for `fract`
  ([`bdf4c12`](https://github.com/Baharis/picometer/commit/bdf4c12d37aa58d6c7ec52c58b150eba17eac498))

- :white_check_mark: Improve `displacement` test to also check for `_U**`, add these to
  `ferrocene2.cif`
  ([`e36f311`](https://github.com/Baharis/picometer/commit/e36f311f51a7507957c03b2fd3bc99836dfd19aa))

- 🔀 Merge pull request #6 from Baharis/development
  ([`8b6d2a6`](https://github.com/Baharis/picometer/commit/8b6d2a62976202ae9ff86851f4a3d73089c0e8cd))

✨ Add fractional `coordinates` and `displacement` parameter commands


## v0.2.0 (2024-10-22)

### :memo:

- :memo: Add missing type hints
  ([`d6cfe05`](https://github.com/Baharis/picometer/commit/d6cfe053e1e75af59a23c171d6f5125d4687a7ec))

- :memo: Update docstrings
  ([`15d0ccf`](https://github.com/Baharis/picometer/commit/15d0ccf91f98d73f2245baca32226a3f222dd880))

### :sparkles:

- :sparkles: .cif files can now be loaded using glob
  ([`86866a0`](https://github.com/Baharis/picometer/commit/86866a0147cd90dc3eb1b4777a5d3d910142e14c))

- :sparkles: `auto_write_unit_cell` when reading cell, add corresponding setting (default True)
  ([`7cf85f0`](https://github.com/Baharis/picometer/commit/7cf85f01472f0a7a88832386f11a7122fadac136))

- :sparkles: `Routine`s can be now saved in a yaml file by converting `Instructions` back to `dict`s
  ([`541a328`](https://github.com/Baharis/picometer/commit/541a328d7ded6ea585d3ce524ea893b3dc3077a6))

- :sparkles: Add logging, used by `__main__` or when `add_file_handler` is called
  ([`49e8a82`](https://github.com/Baharis/picometer/commit/49e8a82609b4a98728c514733b008995fb04814e))

- :sparkles: Add option and tests to save routine history
  ([`8bd79ec`](https://github.com/Baharis/picometer/commit/8bd79ec40ff218ef7a038cdc37e88513de175395))

- :sparkles: Dihedral angles are now handled explicitly via 'dihedral' keyword/handler.
  ([`9364084`](https://github.com/Baharis/picometer/commit/9364084386d97365ce8a452d349430dc83a5b7c2))

### Other

- :coffin: Remove unused process method registration decorators, main
  ([`17ae683`](https://github.com/Baharis/picometer/commit/17ae68361d07f959135082b3d25ad06641dc199c))

- :fire: Clean newly unused code, imports
  ([`a224000`](https://github.com/Baharis/picometer/commit/a2240004b06a2aa820cebeb65da9f1ecddcf1734))

- :recycle: Generalize, make OOM code responsible for handling instructions
  ([`e0fa239`](https://github.com/Baharis/picometer/commit/e0fa239cd4ed22bcf515f4730abad8549aa15620))

- :rotating_light: Fix flake8 linting issues, mostly with `instructions.py`
  ([`bdf203e`](https://github.com/Baharis/picometer/commit/bdf203ee1d35f6c107d9a53c3c9490324df82ceb))

- :white_check_mark: Fix logging tests where closing file in temp dir removes it
  ([`85e04e2`](https://github.com/Baharis/picometer/commit/85e04e2a6ea1f5f165747dbb6bbe99eae8555a7f))

- Merge pull request #5 from Baharis/development
  ([`63d0810`](https://github.com/Baharis/picometer/commit/63d081097275cb851bbd4d6f72cdaa158cbc6280))

:sparkles: Improve `Routine`, `load`ing, add logging, fix dihedral handling


## v0.1.3 (2024-10-16)

### :bug:

- :bug: Fix: dihedral angles were always positive
  ([`a5e41f1`](https://github.com/Baharis/picometer/commit/a5e41f177ebc9c5ad8ac5ca67369af7e8d324164))

### :memo:

- :memo: Document `are_(syn/anti)parallel`, `are_perpendicular` func
  ([`ce2c5d2`](https://github.com/Baharis/picometer/commit/ce2c5d2aa549bf51e29795b664b851ce81826ac4))

### Other

- :green_heart: semantic_release: prepend version commits with :bookmark:
  ([`e080063`](https://github.com/Baharis/picometer/commit/e080063bea1c532890bf3b4f7f18747bf6e9c237))

- :white_check_mark: Add tests for explicit syn- and anti-parallelism
  ([`12d815c`](https://github.com/Baharis/picometer/commit/12d815c4e01fd54df4f81c6f31ee8d93e750dbb8))

- :white_check_mark: Explicitly, separately test for + and - dihedrals
  ([`0da665c`](https://github.com/Baharis/picometer/commit/0da665c653fd61f9025c348518c243a75841dd52))

- 🔀 Merge pull request #4 from Baharis/signed_dihedrals
  ([`fe9c262`](https://github.com/Baharis/picometer/commit/fe9c26232ea441a25836213023c85ea83dadb052))

🐛 Fix: dihedral angles were always positive, add tests


## v0.1.2 (2024-10-16)

### :arrow_down:

- :arrow_down: Slightly relax dependencies
  ([`bb81fc8`](https://github.com/Baharis/picometer/commit/bb81fc8480779b7c6d37714d7b2119bf6cd14d53))

### :memo:

- :memo: Update `example.ipynb` to reflect current `README.md`
  ([`506b613`](https://github.com/Baharis/picometer/commit/506b613c00e560b21652e9a20a9413115f93ddfd))

### Other

- 0.1.2
  ([`2a2b66b`](https://github.com/Baharis/picometer/commit/2a2b66b026ff7ec130a69c1185aa6f268be06bd3))

Automatically generated by python-semantic-release

- :art: Fix linting issue in `test_shapes.py`
  ([`0670d9a`](https://github.com/Baharis/picometer/commit/0670d9a0ccc16002ab80cbb74ed4eacb8d005d43))

- :construction_worker: Align semantic release parser with `https://gitmoji.dev/` spec
  ([`7167bf3`](https://github.com/Baharis/picometer/commit/7167bf3e7e6b055325618651ec0eec7ae3df16e0))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`e4a69d3`](https://github.com/Baharis/picometer/commit/e4a69d3957b734ff54e6eb6e5a28f9ad863ee367))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`cba1b20`](https://github.com/Baharis/picometer/commit/cba1b204898dabf9dfef4d7b4e94c38d45444c55))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`da8af3b`](https://github.com/Baharis/picometer/commit/da8af3b88b284f1230945a91c6f64652bcd918b4))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`753d166`](https://github.com/Baharis/picometer/commit/753d166bd52b6bd157ddc05ca2f3ce3cba11cd3d))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`f41887b`](https://github.com/Baharis/picometer/commit/f41887bfa138b54894aac3833631492b3c23156a))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`19d8e8b`](https://github.com/Baharis/picometer/commit/19d8e8b04cd8e90181ec8e8525606269e8e7ff84))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`6a127d2`](https://github.com/Baharis/picometer/commit/6a127d229c7d1ed9abb45fc53591de6e0e94e33d))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`d157b28`](https://github.com/Baharis/picometer/commit/d157b28a2eff84e1d33f7fa1a15cde0453c3013a))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`1d4b6ed`](https://github.com/Baharis/picometer/commit/1d4b6ed55494904a1b6ea7dd16198ec4b5f15abc))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`e1b9df6`](https://github.com/Baharis/picometer/commit/e1b9df60974b09f13d707ca58dfbc548924643be))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`48fe646`](https://github.com/Baharis/picometer/commit/48fe646844ae701fa8c958c511b44420c87e4038))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`32067b2`](https://github.com/Baharis/picometer/commit/32067b2e4426721e5d4bcc96e15b04abe92043e5))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`b0ea81b`](https://github.com/Baharis/picometer/commit/b0ea81bed980d564d3df80691e67873cbdb84c7b))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`910ab84`](https://github.com/Baharis/picometer/commit/910ab84d8096ddb9bcab68d99e22c13ec661b4fc))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`a63e23e`](https://github.com/Baharis/picometer/commit/a63e23e22113eb0ef47f678dfefd783f3969386a))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`d4ea263`](https://github.com/Baharis/picometer/commit/d4ea26395e88b7ed2225894b3d0f0c0e82b28bd7))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`851fa66`](https://github.com/Baharis/picometer/commit/851fa665f1ad94bd013694c9413280fb41b315d2))

- :construction_worker: Run all tests only on PR, 1 otherwise
  ([`2a25d4d`](https://github.com/Baharis/picometer/commit/2a25d4dca2011f8665cfb37c23a9fa1f97d819e8))

- :fire: Remove `picometer_process.py` superseded by `__main__.py`
  ([`f8e1af8`](https://github.com/Baharis/picometer/commit/f8e1af88e84ad53a80d5a7be4610656437e6e2d1))

- :fire: Remove `requirements.dev.txt` superseded by poetry
  ([`b1d9a65`](https://github.com/Baharis/picometer/commit/b1d9a65b2db49f7e82d6c58512e4e1dcc9eb106e))

- :green_heart: Don't specify python version in step name if variable
  ([`67b2703`](https://github.com/Baharis/picometer/commit/67b2703dc238f920bd573d15764c984dffbb65e7))

- :green_heart: Fix-add "tool.semantic_release.commit_parser_options" config
  ([`bc9ac5a`](https://github.com/Baharis/picometer/commit/bc9ac5a1730105b853603496a4733f6cac1a80a6))

- :green_heart: Force reinstall pip to version before 24.1
  ([`6b75080`](https://github.com/Baharis/picometer/commit/6b75080a9f7048048e74fd2c4aac13df10b48568))

- :green_heart: Force reinstall pip to version before 24.1
  ([`5bd3972`](https://github.com/Baharis/picometer/commit/5bd3972ff0d6b9814fe0b96139b1c86c9b886b5d))

- :truck: Move `CONDUCT.md` to `CODE_OF_CONDUCT.md`
  ([`6f465f8`](https://github.com/Baharis/picometer/commit/6f465f83495b83f8649c67df4d5ae8bf1ab422e7))

- Merge pull request #3 from Baharis/development
  ([`7f95c3f`](https://github.com/Baharis/picometer/commit/7f95c3f60bbae3c37638c416faf01cfdb3cef41a))

:construction_worker: Clear unused code, run all tests only on PR


## v0.1.1 (2024-10-15)

### Other

- 0.1.1
  ([`3045fc5`](https://github.com/Baharis/picometer/commit/3045fc57b7ee293a570aec89dfdce3eb566dfd88))

Automatically generated by python-semantic-release

- :fire: Remove failed attempt at semantic versioning check in CI
  ([`b38b1be`](https://github.com/Baharis/picometer/commit/b38b1bec5580bb0e185b4f6d72fc0e72282c8bcd))

- :green_heart: Add write permissions to the GitHub CD actions
  ([`c8bd378`](https://github.com/Baharis/picometer/commit/c8bd3787ad7e9aec7fd818d1f15ef0c18b92b9a9))

- :green_heart: During CD, checkout with ssh-key to avoid master protection
  ([`3abee66`](https://github.com/Baharis/picometer/commit/3abee665b4f5d5fb9ea921b0d3284f360ecb83dc))

- :green_heart: Upgrade deprecated `codecov/codecov-action@v3` to `v4`
  ([`9a6bb0d`](https://github.com/Baharis/picometer/commit/9a6bb0d566974e98c1789fd7f2fd24291723f4f1))

- :green_heart: Upgrade to `actions/setup-python@v5`, wrap python-version "1.10"
  ([`f644b86`](https://github.com/Baharis/picometer/commit/f644b86f31c5b18a52e9fa34a69fe16e290a1abd))

- Merge branch 'development'
  ([`b82347b`](https://github.com/Baharis/picometer/commit/b82347bfa6d50d70adf86b695e2afcfcd7a9f13e))

- Merge branch 'master' into development
  ([`7d40f77`](https://github.com/Baharis/picometer/commit/7d40f77a785b5187ab6637b805453fede703bc8e))

- Merge pull request #2 from Baharis/development
  ([`10e2835`](https://github.com/Baharis/picometer/commit/10e283568b41295c458216d902314751b981d999))

:green_heart: Switch to automatic versioning and improve documentation


## v0.1.0 (2024-10-14)

### :bug:

- :bug: Fix command line interface for the package
  ([`a177cba`](https://github.com/Baharis/picometer/commit/a177cba794e57be1d1994f046e694a9fb73f6ba5))

### :memo:

- :memo: Update, add badges to `README.md`
  ([`8459b6f`](https://github.com/Baharis/picometer/commit/8459b6fb7850e7f1f0e1cc09e4181004f43c6a2e))

### Other

- "make sure to set your default shell to bash when on Windows."
  ([`a4cbd41`](https://github.com/Baharis/picometer/commit/a4cbd415dfd8a8b0138219f636df99b6e0897347))

- :fire: Remove `requirements.(dev.)txt` superseded by `pyproject.toml`
  ([`11c3ed4`](https://github.com/Baharis/picometer/commit/11c3ed4b542d042d15f4db736a5cdd048a847ba9))

- `[tool.poetry.dev-dependencies]` is deprecated
  ([`937ace0`](https://github.com/Baharis/picometer/commit/937ace07d59c0f1a829abfe7d1525a7e00c1650f))

- `poetry` cache would require unwanted `poetry.lock`
  ([`16c4317`](https://github.com/Baharis/picometer/commit/16c43174ef3e5911864f52fbf876e67082f00e86))

- Adapt test_write for CI tests
  ([`8ba8165`](https://github.com/Baharis/picometer/commit/8ba8165f5cabc77ccf1ad1c1088ed035174004d9))

- Adapt test_write for CI tests 2
  ([`b71a3c9`](https://github.com/Baharis/picometer/commit/b71a3c9d5bab25131bfea7f434b5c5f50f78cd14))

- Adapt test_write for CI tests 3
  ([`fabc9b2`](https://github.com/Baharis/picometer/commit/fabc9b22c061847c21eed5266b490eb0aa0f382f))

- Adapt whitespace in `__init__`
  ([`e65d4a1`](https://github.com/Baharis/picometer/commit/e65d4a1b1e319262bea459b93a92cda51c33c350))

- Add (modified) files suggested by `cookiecutter`, `py-pkgs-cookiecutter`
  ([`fb4321c`](https://github.com/Baharis/picometer/commit/fb4321c492303139fe2f0c2f7a7ebf064c03c178))

- Add `CODECOV_TOKEN` to github action
  ([`cf212b6`](https://github.com/Baharis/picometer/commit/cf212b6703ec8037268c8528c2e6deeca2a4b027))

- Add `python-semantic-release` as a dev dependency
  ([`b03c659`](https://github.com/Baharis/picometer/commit/b03c659d202dbb00e3a59c9b8961654035a5f1e5))

- Add continuous integration, documentation, packaging by `poetry`
  ([#1](https://github.com/Baharis/picometer/pull/1),
  [`438e8fe`](https://github.com/Baharis/picometer/commit/438e8fe2665082e3241fec579f76ec82d38e6238))

* Add (modified) files suggested by `cookiecutter`, `py-pkgs-cookiecutter`

* Rename outer picometer file to avoid name conflict

* Explicitely install flake8 (might be redundant w/ poetry)

* Move requirements to `pyproject.toml` to be handled by poetry

* Adapt whitespace in `__init__`

* Run all tests for picometer

* Add sphinx and pytest-cov for coverage/documentation

* Add sphinx and pytest-cov to `pyproject.toml`

* Add sphinx dependencies

* Sphinx `autoapi_dirs` shouldn't look for picometer in scr/ directory

* `[tool.poetry.dev-dependencies]` is deprecated

* Since picometer is to be a library, don't commit `poetry.lock`

* Don't cap dependency versions: https://iscinumpy.dev/post/bound-version-constraints/

* Lock python version to <4, add jupyter to dev

* Allow picometer to work on hypothetical python 4

* Explicitely specify that docs = tests + picometer

* Rename GitHub workflow files to be more informative

* Theoretically poetry should install dev dependencies

* Install dev dependencies group w/ poetry action

* Tweak, update flake8, codecov GitHub actions

* Preemptively add some badges

* Add `CODECOV_TOKEN` to github action

* Docs: once on master, should work

* Update version release date

* Add snippet for later GitHub CD

- Add default GitHub testing action as in `python-app.yml`
  ([`96cfe02`](https://github.com/Baharis/picometer/commit/96cfe02354f52bba62e28fde9c2e23a473959a6c))

- Add simple `Settings()` tests
  ([`ffdc6c7`](https://github.com/Baharis/picometer/commit/ffdc6c72f2d831c8bbc4c0e0d66a7eacd947c179))

- Add simple version counter
  ([`dfa16ac`](https://github.com/Baharis/picometer/commit/dfa16ac45ac794aa25126e306e28857738c6b506))

- Add snippet for later GitHub CD
  ([`bb262a8`](https://github.com/Baharis/picometer/commit/bb262a841dec0fc7f10fc354416f10d49c8959b4))

- Add some applications of "at" syntax, doesn't work for locators
  ([`0f93057`](https://github.com/Baharis/picometer/commit/0f930576655e6a0535ed15ce9442ffcf1d0357f0))

- Add some initial basic logging ideas
  ([`c202d3b`](https://github.com/Baharis/picometer/commit/c202d3b8541c84762c92e0d4445c78653d496c2c))

- Add some sample files, tests for ferrocene
  ([`63d62fd`](https://github.com/Baharis/picometer/commit/63d62fd2a6f598c8881e98c13cf33fcf8b6bf966))

- Add sphinx and pytest-cov for coverage/documentation
  ([`4178687`](https://github.com/Baharis/picometer/commit/4178687de013baa95d7c83b1c23f1eabb4a889c4))

- Add sphinx and pytest-cov to `pyproject.toml`
  ([`996b2e3`](https://github.com/Baharis/picometer/commit/996b2e3edf34a20fa436c17f51bfd4b9e9df35c9))

- Add sphinx dependencies
  ([`f35a19b`](https://github.com/Baharis/picometer/commit/f35a19b7538467b03a822143965ca147914d1268))

- Allow picometer to work on hypothetical python 4
  ([`3c040bc`](https://github.com/Baharis/picometer/commit/3c040bcb21e032388610071a35f1771f9b77835b))

- Allow semantic release to look at development branch
  ([`e93edda`](https://github.com/Baharis/picometer/commit/e93edda3939bc14e7dee7323ffba882de64dc9d1))

- Apply style suggestions proposed by flake8
  ([`e716728`](https://github.com/Baharis/picometer/commit/e71672899526652027f6c39751893eaab1f71ab2))

- Atomset is now a "spatial-kind implicit directionless" Shape
  ([`6ed4fa9`](https://github.com/Baharis/picometer/commit/6ed4fa95ba8b826b31278494680ede6a5450c84c))

- Calling `select` with no args or `label=None` clears selection
  ([`680fc1b`](https://github.com/Baharis/picometer/commit/680fc1b3539299ebed67236fdc9b12202b866ed9))

- Check out needs to preceed setup with poetry
  ([`183d2a5`](https://github.com/Baharis/picometer/commit/183d2a5cb6e206c69a46c2b947443789bcb57f2f))

- Comment `test_ferrocene.yaml` and remove redundant `ferrocene.yaml`
  ([`0e2779d`](https://github.com/Baharis/picometer/commit/0e2779dfcfafdcca970291086c8ba82af000d13a))

- Correctly return plane/line type, angles between AtomSets
  ([`a2acd07`](https://github.com/Baharis/picometer/commit/a2acd07f908fb06e28fad146f6d73f4e26aa546b))

- Create example.yaml file with intended workflow
  ([`5d640b3`](https://github.com/Baharis/picometer/commit/5d640b3c10095e4b8fc072e9359c04992cf1d304))

- Docs: once on master, should work
  ([`2e0b378`](https://github.com/Baharis/picometer/commit/2e0b378de7090911b9a41b8a81162de0f202bfdb))

- Don't cap dependency versions: https://iscinumpy.dev/post/bound-version-constraints/
  ([`5d11569`](https://github.com/Baharis/picometer/commit/5d11569a057d1acab7021ae6cb79f1360fca19ae))

- Downgrade pip to use "bad metadata" version of hikari
  ([`11b5032`](https://github.com/Baharis/picometer/commit/11b503236677ff5202231033760ebfcde2517bea))

- Explicitely install flake8 (might be redundant w/ poetry)
  ([`d852105`](https://github.com/Baharis/picometer/commit/d85210541f9d06c4fc10809c3d8d5f0acd8cd36b))

- Explicitely specify that docs = tests + picometer
  ([`26f25be`](https://github.com/Baharis/picometer/commit/26f25bee86bf3551115d725cf9623cbcb3dd1db4))

- Fix mess with naming, alias functionality
  ([`f928d10`](https://github.com/Baharis/picometer/commit/f928d100acdafbd7d6049f1275bc8b9c549cb091))

- Fix tests to account for numeric differences across machines
  ([`5950382`](https://github.com/Baharis/picometer/commit/5950382e222a4935536830d9bfd47b1ebca656ae))

- Fix typo in mainb file input
  ([`14c8037`](https://github.com/Baharis/picometer/commit/14c80375e3f39016cd059cbf5eb2b60a7168d97b))

- Flake8 fix, TODO rethink test resources for GitHub actions
  ([`4863afd`](https://github.com/Baharis/picometer/commit/4863afd5fecd214187ae451aa041cb02193648a6))

- Force tests to install hikari 0.2.3 despite "invalid metadata"
  ([`b680b3a`](https://github.com/Baharis/picometer/commit/b680b3a1c3fb9b61b6c52832ae931616ecf6a548))

- Force tests to install hikari 0.2.3 despite "invalid metadata" 2
  ([`3e07e7b`](https://github.com/Baharis/picometer/commit/3e07e7b8d6459d95d81386748961e810a16d2c2f))

- Handle settings using a dedicated `UserDict` subclass
  ([`19a6ce9`](https://github.com/Baharis/picometer/commit/19a6ce9fb1f1028c2a4fb4b5bfee311def7f8310))

- Idea for clearer input syntax rework
  ([`5c06e4c`](https://github.com/Baharis/picometer/commit/5c06e4c1913a3bc48f48ce4219daa164d7687153))

- Implement `continuous-deployment` with Python Semantic Release
  ([`d34a43e`](https://github.com/Baharis/picometer/commit/d34a43e4a2420e0fffdb2149fe7cca382d5fbb7b))

- Implement angles between planes, axes, and AtomSets, writing
  ([`88850d4`](https://github.com/Baharis/picometer/commit/88850d4c353fbd6fc6bbf25cae212eeb57fdf71c))

- Implement context aware path handling for CI testing
  ([`f076e7b`](https://github.com/Baharis/picometer/commit/f076e7b96d0b7a957571c7eb628820b7a2f1984b))

- Implement distances between planes, axes, and AtomSets
  ([`5e5f597`](https://github.com/Baharis/picometer/commit/5e5f59727557edf1db35aed7f39d5ea1cce58b25))

- Initial commit
  ([`a6c3de2`](https://github.com/Baharis/picometer/commit/a6c3de23b0fa637f3f4ab162ad3b8ddfe236d730))

- Initial rework of the instruction system
  ([`c20799e`](https://github.com/Baharis/picometer/commit/c20799e60d137d16abe487f017cc2de4d79be237))

- Install dev dependencies group w/ poetry action
  ([`87d84af`](https://github.com/Baharis/picometer/commit/87d84af8fd63a639a27d33d5890da4f21c27781c))

- Lock python version to <4, add jupyter to dev
  ([`422f4b3`](https://github.com/Baharis/picometer/commit/422f4b32bc697b0d245d8832a81b569a56704de0))

- Merge remote-tracking branch 'origin/master'
  ([`e68c8f7`](https://github.com/Baharis/picometer/commit/e68c8f784bc1b4593a36ec9d95cb567a8f317ded))

- Move `parser` capabilities to list-`routine`, adapt tests
  ([`e658b57`](https://github.com/Baharis/picometer/commit/e658b5715d4c864500dfdaaa50e82721683c9643))

- Move ModelStates, processing to individual files
  ([`8a4d362`](https://github.com/Baharis/picometer/commit/8a4d362cd4b188c68d145d0719b08e221c6265ef))

- Move requirements to `pyproject.toml` to be handled by poetry
  ([`305f9a2`](https://github.com/Baharis/picometer/commit/305f9a2949369c0e860e55a9b6410dff9eb8dba5))

- Move test utils to `test_shapes.py`; TODO rethink file structure
  ([`e4216ff`](https://github.com/Baharis/picometer/commit/e4216ffda8f1e9789f92a6ef6cd902dd1267fbc8))

- Ongling generalization, seems like I got a decent framework
  ([`c5bfcf0`](https://github.com/Baharis/picometer/commit/c5bfcf07d10c1805fcc9352d3eb92447ca9d5146))

- Preemptively add some badges
  ([`aa6f968`](https://github.com/Baharis/picometer/commit/aa6f968bc4e7568bdf3c9f576379fae069c5f37d))

- Processes for handling lines & angles + distances & angles between them
  ([`5fe4420`](https://github.com/Baharis/picometer/commit/5fe4420aa5a5b714054c5a1d5578c8e543e66e88))

- Reimplement tests using new syntax
  ([`754a359`](https://github.com/Baharis/picometer/commit/754a3592e9b3ead0781bd58ce8718da88e8f68a1))

- Rename GitHub workflow files to be more informative
  ([`a4726a6`](https://github.com/Baharis/picometer/commit/a4726a6a1e79d7988940e291ea366fa7217f2669))

- Rename jobs to shorter "CI", "CD" to better fit GitHub GUI
  ([`d7268c2`](https://github.com/Baharis/picometer/commit/d7268c2bf73f90c989aaa0f64200ea37b52bc98f))

- Rename outer picometer file to avoid name conflict
  ([`bdf28b6`](https://github.com/Baharis/picometer/commit/bdf28b69cf42be143d7ef9a530c2f610822ae60f))

- Rename setting to more verbose `clear_selection_after_use`
  ([`9af54bc`](https://github.com/Baharis/picometer/commit/9af54bc99258ef8804022c973232170dd7af1f51))

- Rename test/, add `README.md`, update arg. parsing, settings
  ([`77418fa`](https://github.com/Baharis/picometer/commit/77418fa5aeb03dd09874aeb04e971209d8cd8e12))

- Replace previous implementation with the new one
  ([`5a75f59`](https://github.com/Baharis/picometer/commit/5a75f5952c6a66d691b1432671110ec5aabffbc5))

- Rewritten routine as list-of-instructions only, TODO adapt rest of the code
  ([`bba9bba`](https://github.com/Baharis/picometer/commit/bba9bba09c400aa957d4058a8cc6ae44dde04b0e))

- Run all tests for picometer
  ([`850c3b3`](https://github.com/Baharis/picometer/commit/850c3b398e268e556a0ed88bd104fa2b4ace8e72))

- Simple implementation of shapes (and their distances, angles)
  ([`84049fb`](https://github.com/Baharis/picometer/commit/84049fba212662c959d08b2ae02141ff99169a61))

- Since picometer is to be a library, don't commit `poetry.lock`
  ([`5bf107b`](https://github.com/Baharis/picometer/commit/5bf107bfc1b10615ee03c5115244220c06b9bc99))

- Some initial work to try to generalize pirets code
  ([`8b36bb9`](https://github.com/Baharis/picometer/commit/8b36bb923bef510d7d60bb4faa38223225b2d989))

- Sphinx `autoapi_dirs` shouldn't look for picometer in scr/ directory
  ([`7f91887`](https://github.com/Baharis/picometer/commit/7f918872a44ccbf49ca6ec54e388b7ee67bf266b))

- Split tests into multiple files, add tests for `ExplicitShape`s
  ([`3abf2b2`](https://github.com/Baharis/picometer/commit/3abf2b2c3b22135f04fd948c1b4f183d60b6ce03))

- Theoretically poetry should install dev dependencies
  ([`ab3f94a`](https://github.com/Baharis/picometer/commit/ab3f94acb16a8563afc4edf7694b6df6d88fc2a4))

- Tweak, update flake8, codecov GitHub actions
  ([`cfda1ff`](https://github.com/Baharis/picometer/commit/cfda1ff3cde7c124637ecc7302f5c398d14d4214))

- Update example.yaml to allow for concurrent definitions
  ([`8bb075d`](https://github.com/Baharis/picometer/commit/8bb075d65efa389ccd68814eaaa2c9fdcc40f9ba))

- Update python-app.yml
  ([`bcaf7ae`](https://github.com/Baharis/picometer/commit/bcaf7ae73b179bc8e7c68bb707ec3dc855ae1505))

- Update version release date
  ([`1394162`](https://github.com/Baharis/picometer/commit/1394162fd23e65dea18b7982b6805aba4a9a6ce3))

- Use "label" as focus key, test centroid, line, plane
  ([`528ed46`](https://github.com/Baharis/picometer/commit/528ed46ddbc484a0cedbe7f4a5d2b0fd40035b19))
