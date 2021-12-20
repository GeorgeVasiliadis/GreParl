# GreParl
A simple web-app-based Search Engine built on top of the Greek Parliament Proceedings

## Name
Greek Parliament + grep

## Install
1. Clone the repository
1. Create a venv
1. Install dependencies via `pip install -r requirements.txt`
1. Download data files (see below)
1. Fix the known greek-stemmer issue (newer versions will fix have this ready)

## Download Data Files
The required data files that are not shipped along with the package include the search engine's indices and the parliament proceedings' files (aka the  `index` and the `speeches`).

The `index` consists of three files:
1. index
1. index-catalog
1. index-lengths

These files are typically generated from the `speeches` but they are provided ready-to-use for convenience as well. They can be downloaded [here](https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EVh0ldv0LIdEn-wGw1NhemoBCHW3NwfJQ4CG8XNBgqweeg?e=eGhsrq), renamed as shown in the above listing and moved under the project's directory `/greparl/data/index/`.

The `speeches` can be extracted from [this repository](https://github.com/iMEdD-Lab/Greek_Parliament_Proceedings/tree/master/src) and moved under the project's directory `/greparl/data/`, named as `speeches.csv`.

## Run
1. Activate venv
1. Run the start.* script
1. Browse to "http://127.0.0.1:5000/"
