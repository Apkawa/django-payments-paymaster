[![Build Status](https://travis-ci.org/Apkawa/{django-app-template}.svg?branch=master)](https://travis-ci.org/Apkawa/{django-app-template})
[![codecov](https://codecov.io/gh/Apkawa/{django-app-template}/branch/master/graph/badge.svg)](https://codecov.io/gh/Apkawa/{django-app-template})
[![Requirements Status](https://requires.io/github/Apkawa/{django-app-template}/requirements.svg?branch=master)](https://requires.io/github/Apkawa/{django-app-template}/requirements/?branch=master)
[![PyUP](https://pyup.io/repos/github/Apkawa/{django-app-template}/shield.svg)](https://pyup.io/repos/github/Apkawa/{django-app-template})
[![PyPI](https://img.shields.io/pypi/pyversions/{django-app-template}.svg)]()

Template repository for django-app.
After create find and replace 
* `{django-app-template}` to new repository name
* `{example_app}` to new app package name

# Installation

```bash
pip install {django-app-template}

```

or from git

```bash
pip install -e git+https://githib.com/Apkawa/{django-app-template}.git#egg={django-app-template}
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






