# CHANGELOG


## v0.1.1 (2024-10-15)

### Other

* :green_heart: Add write permissions to the GitHub CD actions ([`c8bd378`](https://github.com/Baharis/picometer/commit/c8bd3787ad7e9aec7fd818d1f15ef0c18b92b9a9))

* :green_heart: During CD, checkout with ssh-key to avoid master protection ([`3abee66`](https://github.com/Baharis/picometer/commit/3abee665b4f5d5fb9ea921b0d3284f360ecb83dc))

* Merge branch 'development' ([`b82347b`](https://github.com/Baharis/picometer/commit/b82347bfa6d50d70adf86b695e2afcfcd7a9f13e))

* :green_heart: Upgrade to `actions/setup-python@v5`, wrap python-version "1.10" ([`f644b86`](https://github.com/Baharis/picometer/commit/f644b86f31c5b18a52e9fa34a69fe16e290a1abd))

* :green_heart: Upgrade deprecated `codecov/codecov-action@v3` to `v4` ([`9a6bb0d`](https://github.com/Baharis/picometer/commit/9a6bb0d566974e98c1789fd7f2fd24291723f4f1))

* Merge pull request #2 from Baharis/development

:green_heart: Switch to automatic versioning and improve documentation ([`10e2835`](https://github.com/Baharis/picometer/commit/10e283568b41295c458216d902314751b981d999))

* :fire: Remove failed attempt at semantic versioning check in CI ([`b38b1be`](https://github.com/Baharis/picometer/commit/b38b1bec5580bb0e185b4f6d72fc0e72282c8bcd))

* Merge branch 'master' into development ([`7d40f77`](https://github.com/Baharis/picometer/commit/7d40f77a785b5187ab6637b805453fede703bc8e))


## v0.1.0 (2024-10-14)

### :bug:

* :bug: Fix command line interface for the package ([`a177cba`](https://github.com/Baharis/picometer/commit/a177cba794e57be1d1994f046e694a9fb73f6ba5))

### Other

* Add continuous integration, documentation, packaging by `poetry` (#1)

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

* Add snippet for later GitHub CD ([`438e8fe`](https://github.com/Baharis/picometer/commit/438e8fe2665082e3241fec579f76ec82d38e6238))

* :memo: Update, add badges to `README.md` ([`8459b6f`](https://github.com/Baharis/picometer/commit/8459b6fb7850e7f1f0e1cc09e4181004f43c6a2e))

* :fire: Remove `requirements.(dev.)txt` superseded by `pyproject.toml` ([`11c3ed4`](https://github.com/Baharis/picometer/commit/11c3ed4b542d042d15f4db736a5cdd048a847ba9))

* Allow semantic release to look at development branch ([`e93edda`](https://github.com/Baharis/picometer/commit/e93edda3939bc14e7dee7323ffba882de64dc9d1))

* "Make sure to set your default shell to bash when on Windows." ([`a4cbd41`](https://github.com/Baharis/picometer/commit/a4cbd415dfd8a8b0138219f636df99b6e0897347))

* `poetry` cache would require unwanted `poetry.lock` ([`16c4317`](https://github.com/Baharis/picometer/commit/16c43174ef3e5911864f52fbf876e67082f00e86))

* Rename jobs to shorter "CI", "CD" to better fit GitHub GUI ([`d7268c2`](https://github.com/Baharis/picometer/commit/d7268c2bf73f90c989aaa0f64200ea37b52bc98f))

* Check out needs to preceed setup with poetry ([`183d2a5`](https://github.com/Baharis/picometer/commit/183d2a5cb6e206c69a46c2b947443789bcb57f2f))

* Implement `continuous-deployment` with Python Semantic Release ([`d34a43e`](https://github.com/Baharis/picometer/commit/d34a43e4a2420e0fffdb2149fe7cca382d5fbb7b))

* Add `python-semantic-release` as a dev dependency ([`b03c659`](https://github.com/Baharis/picometer/commit/b03c659d202dbb00e3a59c9b8961654035a5f1e5))

* Add snippet for later GitHub CD ([`bb262a8`](https://github.com/Baharis/picometer/commit/bb262a841dec0fc7f10fc354416f10d49c8959b4))

* Update version release date ([`1394162`](https://github.com/Baharis/picometer/commit/1394162fd23e65dea18b7982b6805aba4a9a6ce3))

* Docs: once on master, should work ([`2e0b378`](https://github.com/Baharis/picometer/commit/2e0b378de7090911b9a41b8a81162de0f202bfdb))

* Add `CODECOV_TOKEN` to github action ([`cf212b6`](https://github.com/Baharis/picometer/commit/cf212b6703ec8037268c8528c2e6deeca2a4b027))

* Preemptively add some badges ([`aa6f968`](https://github.com/Baharis/picometer/commit/aa6f968bc4e7568bdf3c9f576379fae069c5f37d))

* Tweak, update flake8, codecov GitHub actions ([`cfda1ff`](https://github.com/Baharis/picometer/commit/cfda1ff3cde7c124637ecc7302f5c398d14d4214))

* Install dev dependencies group w/ poetry action ([`87d84af`](https://github.com/Baharis/picometer/commit/87d84af8fd63a639a27d33d5890da4f21c27781c))

* Theoretically poetry should install dev dependencies ([`ab3f94a`](https://github.com/Baharis/picometer/commit/ab3f94acb16a8563afc4edf7694b6df6d88fc2a4))

* Rename GitHub workflow files to be more informative ([`a4726a6`](https://github.com/Baharis/picometer/commit/a4726a6a1e79d7988940e291ea366fa7217f2669))

* Explicitely specify that docs = tests + picometer ([`26f25be`](https://github.com/Baharis/picometer/commit/26f25bee86bf3551115d725cf9623cbcb3dd1db4))

* Allow picometer to work on hypothetical python 4 ([`3c040bc`](https://github.com/Baharis/picometer/commit/3c040bcb21e032388610071a35f1771f9b77835b))

* Lock python version to <4, add jupyter to dev ([`422f4b3`](https://github.com/Baharis/picometer/commit/422f4b32bc697b0d245d8832a81b569a56704de0))

* Don't cap dependency versions: https://iscinumpy.dev/post/bound-version-constraints/ ([`5d11569`](https://github.com/Baharis/picometer/commit/5d11569a057d1acab7021ae6cb79f1360fca19ae))

* Since picometer is to be a library, don't commit `poetry.lock` ([`5bf107b`](https://github.com/Baharis/picometer/commit/5bf107bfc1b10615ee03c5115244220c06b9bc99))

* `[tool.poetry.dev-dependencies]` is deprecated ([`937ace0`](https://github.com/Baharis/picometer/commit/937ace07d59c0f1a829abfe7d1525a7e00c1650f))

* Sphinx `autoapi_dirs` shouldn't look for picometer in scr/ directory ([`7f91887`](https://github.com/Baharis/picometer/commit/7f918872a44ccbf49ca6ec54e388b7ee67bf266b))

* Add sphinx dependencies ([`f35a19b`](https://github.com/Baharis/picometer/commit/f35a19b7538467b03a822143965ca147914d1268))

* Add sphinx and pytest-cov to `pyproject.toml` ([`996b2e3`](https://github.com/Baharis/picometer/commit/996b2e3edf34a20fa436c17f51bfd4b9e9df35c9))

* Add sphinx and pytest-cov for coverage/documentation ([`4178687`](https://github.com/Baharis/picometer/commit/4178687de013baa95d7c83b1c23f1eabb4a889c4))

* Run all tests for picometer ([`850c3b3`](https://github.com/Baharis/picometer/commit/850c3b398e268e556a0ed88bd104fa2b4ace8e72))

* Adapt whitespace in `__init__` ([`e65d4a1`](https://github.com/Baharis/picometer/commit/e65d4a1b1e319262bea459b93a92cda51c33c350))

* Move requirements to `pyproject.toml` to be handled by poetry ([`305f9a2`](https://github.com/Baharis/picometer/commit/305f9a2949369c0e860e55a9b6410dff9eb8dba5))

* Explicitely install flake8 (might be redundant w/ poetry) ([`d852105`](https://github.com/Baharis/picometer/commit/d85210541f9d06c4fc10809c3d8d5f0acd8cd36b))

* Rename outer picometer file to avoid name conflict ([`bdf28b6`](https://github.com/Baharis/picometer/commit/bdf28b69cf42be143d7ef9a530c2f610822ae60f))

* Add (modified) files suggested by `cookiecutter`, `py-pkgs-cookiecutter` ([`fb4321c`](https://github.com/Baharis/picometer/commit/fb4321c492303139fe2f0c2f7a7ebf064c03c178))

* Apply style suggestions proposed by flake8 ([`e716728`](https://github.com/Baharis/picometer/commit/e71672899526652027f6c39751893eaab1f71ab2))

* Add simple `Settings()` tests ([`ffdc6c7`](https://github.com/Baharis/picometer/commit/ffdc6c72f2d831c8bbc4c0e0d66a7eacd947c179))

* Add simple version counter ([`dfa16ac`](https://github.com/Baharis/picometer/commit/dfa16ac45ac794aa25126e306e28857738c6b506))

* Move `parser` capabilities to list-`routine`, adapt tests ([`e658b57`](https://github.com/Baharis/picometer/commit/e658b5715d4c864500dfdaaa50e82721683c9643))

* Rewritten routine as list-of-instructions only, TODO adapt rest of the code ([`bba9bba`](https://github.com/Baharis/picometer/commit/bba9bba09c400aa957d4058a8cc6ae44dde04b0e))

* Rename setting to more verbose `clear_selection_after_use` ([`9af54bc`](https://github.com/Baharis/picometer/commit/9af54bc99258ef8804022c973232170dd7af1f51))

* Handle settings using a dedicated `UserDict` subclass ([`19a6ce9`](https://github.com/Baharis/picometer/commit/19a6ce9fb1f1028c2a4fb4b5bfee311def7f8310))

* Comment `test_ferrocene.yaml` and remove redundant `ferrocene.yaml` ([`0e2779d`](https://github.com/Baharis/picometer/commit/0e2779dfcfafdcca970291086c8ba82af000d13a))

* Adapt test_write for CI tests 3 ([`fabc9b2`](https://github.com/Baharis/picometer/commit/fabc9b22c061847c21eed5266b490eb0aa0f382f))

* Adapt test_write for CI tests 2 ([`b71a3c9`](https://github.com/Baharis/picometer/commit/b71a3c9d5bab25131bfea7f434b5c5f50f78cd14))

* Merge remote-tracking branch 'origin/master' ([`e68c8f7`](https://github.com/Baharis/picometer/commit/e68c8f784bc1b4593a36ec9d95cb567a8f317ded))

* Update python-app.yml ([`bcaf7ae`](https://github.com/Baharis/picometer/commit/bcaf7ae73b179bc8e7c68bb707ec3dc855ae1505))

* Downgrade pip to use "bad metadata" version of hikari ([`11b5032`](https://github.com/Baharis/picometer/commit/11b503236677ff5202231033760ebfcde2517bea))

* Force tests to install hikari 0.2.3 despite "invalid metadata" 2 ([`3e07e7b`](https://github.com/Baharis/picometer/commit/3e07e7b8d6459d95d81386748961e810a16d2c2f))

* Adapt test_write for CI tests ([`8ba8165`](https://github.com/Baharis/picometer/commit/8ba8165f5cabc77ccf1ad1c1088ed035174004d9))

* Force tests to install hikari 0.2.3 despite "invalid metadata" ([`b680b3a`](https://github.com/Baharis/picometer/commit/b680b3a1c3fb9b61b6c52832ae931616ecf6a548))

* Implement context aware path handling for CI testing ([`f076e7b`](https://github.com/Baharis/picometer/commit/f076e7b96d0b7a957571c7eb628820b7a2f1984b))

* flake8 fix, TODO rethink test resources for GitHub actions ([`4863afd`](https://github.com/Baharis/picometer/commit/4863afd5fecd214187ae451aa041cb02193648a6))

* Move test utils to `test_shapes.py`; TODO rethink file structure ([`e4216ff`](https://github.com/Baharis/picometer/commit/e4216ffda8f1e9789f92a6ef6cd902dd1267fbc8))

* Add default GitHub testing action as in `python-app.yml` ([`96cfe02`](https://github.com/Baharis/picometer/commit/96cfe02354f52bba62e28fde9c2e23a473959a6c))

* Fix tests to account for numeric differences across machines ([`5950382`](https://github.com/Baharis/picometer/commit/5950382e222a4935536830d9bfd47b1ebca656ae))

* Split tests into multiple files, add tests for `ExplicitShape`s ([`3abf2b2`](https://github.com/Baharis/picometer/commit/3abf2b2c3b22135f04fd948c1b4f183d60b6ce03))

* Calling `select` with no args or `label=None` clears selection ([`680fc1b`](https://github.com/Baharis/picometer/commit/680fc1b3539299ebed67236fdc9b12202b866ed9))

* Rename test/, add `README.md`, update arg. parsing, settings ([`77418fa`](https://github.com/Baharis/picometer/commit/77418fa5aeb03dd09874aeb04e971209d8cd8e12))

* Replace previous implementation with the new one ([`5a75f59`](https://github.com/Baharis/picometer/commit/5a75f5952c6a66d691b1432671110ec5aabffbc5))

* Reimplement tests using new syntax ([`754a359`](https://github.com/Baharis/picometer/commit/754a3592e9b3ead0781bd58ce8718da88e8f68a1))

* Initial rework of the instruction system ([`c20799e`](https://github.com/Baharis/picometer/commit/c20799e60d137d16abe487f017cc2de4d79be237))

* Fix typo in mainb file input ([`14c8037`](https://github.com/Baharis/picometer/commit/14c80375e3f39016cd059cbf5eb2b60a7168d97b))

* Idea for clearer input syntax rework ([`5c06e4c`](https://github.com/Baharis/picometer/commit/5c06e4c1913a3bc48f48ce4219daa164d7687153))

* Add some initial basic logging ideas ([`c202d3b`](https://github.com/Baharis/picometer/commit/c202d3b8541c84762c92e0d4445c78653d496c2c))

* Move ModelStates, processing to individual files ([`8a4d362`](https://github.com/Baharis/picometer/commit/8a4d362cd4b188c68d145d0719b08e221c6265ef))

* Implement angles between planes, axes, and AtomSets, writing ([`88850d4`](https://github.com/Baharis/picometer/commit/88850d4c353fbd6fc6bbf25cae212eeb57fdf71c))

* Implement distances between planes, axes, and AtomSets ([`5e5f597`](https://github.com/Baharis/picometer/commit/5e5f59727557edf1db35aed7f39d5ea1cce58b25))

* Add some applications of "at" syntax, doesn't work for locators ([`0f93057`](https://github.com/Baharis/picometer/commit/0f930576655e6a0535ed15ce9442ffcf1d0357f0))

* Use "label" as focus key, test centroid, line, plane ([`528ed46`](https://github.com/Baharis/picometer/commit/528ed46ddbc484a0cedbe7f4a5d2b0fd40035b19))

* Fix mess with naming, alias functionality ([`f928d10`](https://github.com/Baharis/picometer/commit/f928d100acdafbd7d6049f1275bc8b9c549cb091))

* Add some sample files, tests for ferrocene ([`63d62fd`](https://github.com/Baharis/picometer/commit/63d62fd2a6f598c8881e98c13cf33fcf8b6bf966))

* Correctly return plane/line type, angles between AtomSets ([`a2acd07`](https://github.com/Baharis/picometer/commit/a2acd07f908fb06e28fad146f6d73f4e26aa546b))

* Processes for handling lines & angles + distances & angles between them ([`5fe4420`](https://github.com/Baharis/picometer/commit/5fe4420aa5a5b714054c5a1d5578c8e543e66e88))

* AtomSet is now a "spatial-kind implicit directionless" Shape ([`6ed4fa9`](https://github.com/Baharis/picometer/commit/6ed4fa95ba8b826b31278494680ede6a5450c84c))

* Simple implementation of shapes (and their distances, angles) ([`84049fb`](https://github.com/Baharis/picometer/commit/84049fba212662c959d08b2ae02141ff99169a61))

* Ongling generalization, seems like I got a decent framework ([`c5bfcf0`](https://github.com/Baharis/picometer/commit/c5bfcf07d10c1805fcc9352d3eb92447ca9d5146))

* Some initial work to try to generalize pirets code ([`8b36bb9`](https://github.com/Baharis/picometer/commit/8b36bb923bef510d7d60bb4faa38223225b2d989))

* Update example.yaml to allow for concurrent definitions ([`8bb075d`](https://github.com/Baharis/picometer/commit/8bb075d65efa389ccd68814eaaa2c9fdcc40f9ba))

* Create example.yaml file with intended workflow ([`5d640b3`](https://github.com/Baharis/picometer/commit/5d640b3c10095e4b8fc072e9359c04992cf1d304))

* Initial commit ([`a6c3de2`](https://github.com/Baharis/picometer/commit/a6c3de23b0fa637f3f4ab162ad3b8ddfe236d730))
