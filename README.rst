python-qrplatba
===============

.. image:: https://badge.fury.io/py/qrplatba.png
    :target: http://badge.fury.io/py/qrplatba

QR platba SVG QR code and SPD string generator.

.. image:: https://raw.github.com/viktorstiskala/python-qrplatba/gh-pages/example.png
    :target: http://viktorstiskala.github.io/python-qrplatba/example.svg

See http://qr-platba.cz/pro-vyvojare/ for more information about the specification (available only in czech).

.. code-block:: python

    from qrplatba import QRPlatbaGenerator
    from datetime import datetime, timedelta


    due = datetime.now() + timedelta(days=14)
    generator = QRPlatbaGenerator('123456789/0123', 400.56, x_vs=2034456, message='text', due_date=due)
    img = generator.make_image()
    img.save('example.svg')
    
Installation
------------

To install qrplatba, simply:

.. code-block:: bash

    $ pip install qrplatba
    
Note on image file formats
--------------------------

This module generates SVG file which is an XML-based vector image format. You can use various libraries and/or utilities to convert it to other vector or bitmap image formats. Below is an example how to use ``libRSVG`` to convert SVG images.

libRSVG
~~~~~~~

`libRSVG <https://wiki.gnome.org/action/show/Projects/LibRsvg?action=show>`_ renders SVG files using cairo and supports many output image formats. It can also be used directly in console with ``rsvg-convert`` command.

.. code-block:: bash

    $ rsvg-convert -f pdf example.svg -o example.pdf

License
-------

This software is licensed under MPL 2.0.

- http://mozilla.org/MPL/2.0/
- http://www.mozilla.org/MPL/2.0/FAQ.html#use
