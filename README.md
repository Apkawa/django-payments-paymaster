[![Build Status](https://travis-ci.org/Apkawa/django-payments-paymaster.svg?branch=master)](https://travis-ci.org/Apkawa/django-payments-paymaster)
[![codecov](https://codecov.io/gh/Apkawa/django-payments-paymaster/branch/master/graph/badge.svg)](https://codecov.io/gh/Apkawa/django-payments-paymaster)
[![Requirements Status](https://requires.io/github/Apkawa/django-payments-paymaster/requirements.svg?branch=master)](https://requires.io/github/Apkawa/django-payments-paymaster/requirements/?branch=master)
[![PyUP](https://pyup.io/repos/github/Apkawa/django-payments-paymaster/shield.svg)](https://pyup.io/repos/github/Apkawa/django-payments-paymaster)
[![PyPI](https://img.shields.io/pypi/pyversions/django-payments-paymaster.svg)]()

Template repository for django-app.
After create find and replace 
* `django-payments-paymaster` to new repository name
* `payments_paymaster` to new app package name

# Installation

```bash
pip install django-payments-paymaster

```

or from git

```bash
pip install -e git+https://githib.com/Apkawa/django-payments-paymaster.git#egg=django-payments-paymaster
```

## Django and python version

| Python<br/>Django |        3.5         |      3.6           |      3.7           |       3.8          |
|:-----------------:|--------------------|--------------------|--------------------|--------------------|
| 1.8               |       :x:          |      :x:           |       :x:          |      :x:           |
| 1.11              | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |      :x:           |
| 2.2               | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| 3.0               |       :x:          | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |


# Usage



# Contributing

## run example app

```bash
pip install -r requirements.txt
./test/manage.py migrate
./test/manage.py runserver
```

## run tests

```bash
pip install -r requirements.txt
pytest
tox
```

## Update version

```bash
python setup.py bumpversion
```

## publish pypi

```bash
python setup.py publish
```






