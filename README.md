
Installation
============

### System requirements

- python3.3+
- python3-dev (3.3+ for newrelic)
- libffi-dev (for bcrypt)

### Babel

Needs to be installed from github to get version 2.0dev. After pip install:

cd ~/.envs/superglot/src/babel
python setup.py import_cldr

### NLTK

Needs corpus (nltk_data).
With GUI:

```python
import nltk
nltk.download()
```