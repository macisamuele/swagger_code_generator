===============
swagger-to-java
===============

.. image:: https://img.shields.io/travis/macisamuele/swagger_code_generator.svg
        :target: https://travis-ci.org/macisamuele/swagger_code_generator

.. image:: https://img.shields.io/coveralls/macisamuele/swagger_code_generator.svg
  :target: https://coveralls.io/r/macisamuele/swagger_code_generator

.. image:: https://img.shields.io/pypi/v/swagger_code_generator.svg
        :target: https://pypi.python.org/pypi/swagger_code_generator

.. image:: https://readthedocs.org/projects/swagger-to-java/badge/?version=latest
        :target: https://swagger-to-java.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/macisamuele/swagger_code_generator/shield.svg
     :target: https://pyup.io/repos/github/macisamuele/swagger_code_generator/
     :alt: Updates


A simple tool that allows to generate native classes on your programming language starting from the response models of a Swagger spec.

NOTE
----

At the moment the project is a Work In Progress; for this reason documentation and availability on pypi is not guaranteed.

Features
--------
* Modular tool: allow additional language support

Documentation
-------------

Documentation is available at `readthedocs.org <http://swagger-to-java.readthedocs.org>`__


Installation
------------

::

    $ pip install swagger-to-java


Projects Dependencies
---------------------
* bravado_.

Development
===========
    Code is documented using Sphinx_

    aactivator_ is used for easily activate and deactivate the virtual environment

    `pre-commit`_ is used to keep a consistent style within the respository

    tox_ is used for standardized testing

    `venv-update`_ is used to cache python dependencies making faster the creation of virtual enviroments

    virtualenv_ is recommended to keep dependencies and libraries isolated.


Setup
-----

::

    # Install all the dependencies needed for development
    make development


Contributing
------------

1. Fork it ( http://github.com/macisamuele/swagger_code_generator/fork )
2. Create your feature branch (``git checkout -b my-new-feature``)
3. Add your modifications
4. Add short summary of your modifications on ``CHANGELOG.rst``
5. Commit your changes (``git commit -m "Add some feature"``)
6. Push to the branch (``git push <remote> my-new-feature``)
7. Create new Pull Request

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `macisamuele/python-package-template`_ project template.

License
-------

| Copyright (c) 2017, Maci Samuele All rights reserved.

swagger_code_generator is licensed with a `BSD 3-Clause License`_.

.. _aactivator: https://github.com/Yelp/aactivator/
.. _bravado: https://github.com/Yelp/bravado/
.. _`BSD 3-Clause License`: https://opensource.org/licenses/BSD-3-Clause
.. _Cookiecutter: https://github.com/audreyr/cookiecutter/
.. _`macisamuele/python-package-template`: https://github.com/macisamuele/python-package-template/
.. _`pre-commit`: https://github.com/pre-commit/pre-commit/
.. _Sphinx: http://sphinx-doc.org/
.. _`venv-update`: https://github.com/Yelp/venv-update/
.. _virtualenv: http://virtualenv.readthedocs.io/en/latest/
.. _tox: https://tox.readthedocs.org/en/latest/
