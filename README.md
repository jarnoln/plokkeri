# Plokkeri

[![CircleCI](https://circleci.com/gh/jarnoln/plokkeri.svg?style=shield)](https://circleci.com/gh/jarnoln/plokkeri)
[![codecov](https://codecov.io/gh/jarnoln/plokkeri/branch/master/graph/badge.svg)](https://codecov.io/gh/jarnoln/plokkeri)

Simple blogging platform by [Jarno Luoma-Nirva](http://jln.fi).
[GitHub](https://github.com/jarnoln/plokkeri)

Using
-----
 - [Python](https://www.python.org/)(3.5) and [Django](https://www.djangoproject.com/)(2.0)
 - [GitHub](https://github.com/jarnoln/plokkeri/) for version control
 - [Ansible](https://www.ansible.com/) for provisioning servers
 - [Fabric](http://www.fabfile.org/) for automated deployments
 - [CircleCI](https://circleci.com/gh/jarnoln/plokkeri) for test automation
 - [codecov.io](https://codecov.io/gh/jarnoln/plokkeri) for test coverage tracking
 - [django-allauth](http://django-allauth.readthedocs.io/en/latest/) for 3rd party authentication 
 - [DigitalOcean](https://www.digitalocean.com/) for servers
 - [PyCharm](https://www.jetbrains.com/pycharm/) as IDE
 - [Obey the testing goat](https://www.obeythetestinggoat.com/) for guidance and inspiration

Installing
----------

1. [Install Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html)

2. Get sources:

    git clone https://github.com/jarnoln/plokkeri.git

3. Add your host to ansible/inventory. Then:

    ansible-playbook -i ansible/inventory ansible/provision-deb.yaml

    fab -f fabfile.py deploy:host=user@host


Set up development environment
------------------------------

Get sources:

    git clone https://github.com/jarnoln/plokkeri.git

Create virtual environment and install Python packages:

    mkvirtualenv -p /usr/bin/python3 plokkeri
    pip install -r requirements.txt

Generate password:

    python plokkeri/generate_passwords.py plokkeri/passwords.py

Initialize DB:

    ./manage.py migrate
    ./manage.py makemigrations plok
    ./manage.py migrate

Run tests:

    ./manage.py test

If tests pass, you should be good to go.

Run development server:

    ./manage.py runserver

Now should be able to see Plokkeri in your browser at http://127.0.0.1:8000/
