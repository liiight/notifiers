About :mod:`notifiers`
======================

The problem
-----------

While I was working on a different project, I needed to enable its users to send notifications.
Soon I discovered that this was a project by itself, discovering and implementing different provider API, testing it, relying on outdated documentation at times and etc. It was quite the endeavour.
Some providers offered their own SDK packages, but that meant adding more dependencies to an already dependency rich project, which was not ideal.
There has to be a better way, right?

The solution
------------
Enter :mod:`notifiers`. A common interface to many, many notification providers, with a minimal set of dependencies (just :mod:`requests`, :mod:`jsonschema` and :mod:`click` for CLI operations)

The interface
-------------
Right out of the gate there was an issue of consistent naming. Different API providers have different names for similar properties.
For example, one provider can name its API key as ``api_key``, another as ``token``, the third as ``apikey`` and etc.
The solution I chose was to be as fateful to the original API properties as possible, with the only exception being the ``message`` property,
which is shared among all notifiers and replaced internally as needed.





