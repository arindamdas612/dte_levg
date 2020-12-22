# DTE Leverage Report application

## Prerequisite

Make sure virtualenv package is available, if not use the below command

```sh
$ pip install virtualenv

```
## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/arindamdas612/dte_levg.git
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ virtualenv venv
$ source env/bin/activate (Linux or Mac)
> & <path-to-virtual-env>/venv/Scripts/Activate.ps1 (Windows only)
```

Then install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```
Note the `(venv)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`.

Once `pip` has finished downloading the dependencies:
```sh
(venv)$ cd src
```

Create the database for the application
```sh
(venv)$ python manage.py migrate
```

Create a superuser for the application
```sh
(venv)$ python manage.py createsuperuser
```

Start the local server
```sh
(venv)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`.