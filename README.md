python-web-server
=================

Python web server that runs at http://dabo.guru/py/ (proxied through apache2)

If you POST to /notify, it'll send a pushbullet notification to a given device.

If you GET to /oauth/?key=value, it'll give you a base64 encoded string containing a json object of all of the GET parameters.

Try it out at http://dabo.guru/py/oauth/?key=value

Or POST to http://dabo.guru/py/notify, and I'll get a notification on my phone. There's an example of using this in javascript at http://dabo.guru/
