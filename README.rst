=============
travel_mapper
=============


.. image:: https://img.shields.io/pypi/v/travel_mapper.svg
        :target: https://pypi.python.org/pypi/travel_mapper

.. image:: https://img.shields.io/travis/rmartinshort/travel_mapper.svg
        :target: https://travis-ci.com/rmartinshort/travel_mapper

.. image:: https://readthedocs.org/projects/travel-mapper/badge/?version=latest
        :target: https://travel-mapper.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




A travel agent that uses calls to OpenAI to build an itinerary and then Google Maps API to gather directions.

To test it out in a python console, try the following

```
from travel_mapper.test_without_gradio import test
test()
```

This will use a default query and is useful to check if everything is installed correctly. You can also run
`test()` with a custom query, as in `test(query="A 2 day trip around Los Angeles that includes the best views of the Hollywood sign")`.

To run the gradio app, which allows more interactions with the models, run the following from a terminal

```python travel_mapper/user_interface/driver.py```

This will open the app locally.

* Free software: MIT license
* Documentation: https://travel-mapper.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
