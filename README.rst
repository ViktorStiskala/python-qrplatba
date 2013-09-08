python-qrplatba
===============

.. image:: https://badge.fury.io/py/qrplatba.png
    :target: http://badge.fury.io/py/qrplatba

QR platba SVG QR code and SPD string generator.

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

License
-------

This software is licensed under MPL 2.0.

http://mozilla.org/MPL/2.0/
http://www.mozilla.org/MPL/2.0/FAQ.html#use
