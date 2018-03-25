About
=====

The problem
-----------

While I was working on a different project, I needed to enable its users to send notifications.
Soon I discovered that this was a project by itself, discovering and implementing different provider API, testing it, relying on outdated documentation at times and etc. It was quite the endeavour.
Some providers offered their own SDK packages, but that meant adding more dependencies to an already dependency rich project, which was not ideal.
There has to be a better way, right?

The solution
------------
Enter :mod:`notifiers`. A common interface to many, many notification providers, with a minimal set of dependencies (just :mod:`jsonschema`, :mod:`requests`, and :mod:`click` for CLI operations)

The interface
-------------
Right out of the gate there was an issue of consistent naming. Different API providers have different names for similar properties.
For example, one provider can name its API key as ``api_key``, another as ``token``, the third as ``apikey`` and etc.
The solution I chose was to be as fateful to the original API properties as possible, with the only exception being the ``message`` property,
which is shared among all notifiers and replaced internally as needed.

What this is
------------
A general wrapper for a variety of 3rd party providers and built in ones (like SMTP) aimed solely at sending notifications.

Who is this for
---------------
* Developers aiming to integrate 3rd party notifications into their application
* Script makes aiming to enable 3rd party notification abilities, either via python script or any CLI script
* Anyone that want to programmatically send notification and not be concerned about familiarizing themselves with 3rd party APIs or built in abilities

What this isn't
---------------
Many providers API enable many other capabilities other than sending notification. None of those will be handled by this module as it's outside its scope. If you need API access other than sending notification, look into implementing the 3rd party API directly, or using an SDK if available.



