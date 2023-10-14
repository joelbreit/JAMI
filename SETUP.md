# Initial Setup Process

## Create venv

1. `python -m venv env_for_jami`
2. `source env_for_jami/bin/activate`

## Install Dependencies

### (First Time)
1. `pip install music21`
2. `pip freeze > requirements.txt`

### Subsequent Setup

1. `pip install -r requirements.txt`