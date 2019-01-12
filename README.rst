|Downloads|

hecho
=====

hecho is a fast and simple HTTP echo server.

An example is running on "http://hecho.bigode.net/".

It uses Falcon_ HTTP library and Bjoern_ WSGI server to serve thousands
requests per second using just one CPU Core and approximately 15MB of RAM.

The response is a "prettified" json containing the request.

Simple request/response example::

    $ curl --header "Content-Type: application/json" \
        --request POST --data '{"user": "john", "pass": "1234"}' \
        http://localhost:8000?p=param

    {
        "headers": {
            "ACCEPT": "*/*",
            "CONTENT-LENGTH": "32",
            "CONTENT-TYPE": "application/json",
            "HOST": "localhost:8000",
            "USER-AGENT": "curl/7.19.7 (x86_64-redhat-linux-gnu) libcurl/7.19.7 NSS/3.27.1 zlib/1.2.3 libidn/1.18 libssh2/1.4.2"
        },
        "json": {
            "pass": "1234",
            "user": "john"
        },
        "method": "POST",
        "origin": "127.0.0.1",
        "params": {
            "p": "param"
        },
        "url": "http://localhost:8000/?p=param"
    }

It supports get, post, put, patch and delete methods.

The request data must be JSON or x-www-form-urlencoded (standard simple post).


Notes
=====

- Works on Python 2.7 and Python3.4+


Install
=======

Install using pip::

    pip install hecho


Usage
=====

::

    Usage: hecho [options] start|stop|restart

    simple and fast http echo server

    Options:
    --version           show program's version number and exit
    -h, --help          show this help message and exit
    -l ADDRESS          address to listen (default: localhost)
    -p PORT             application port (default: 8000)
    --log-path=LOGPATH  logfile path (default: ~/.hecho/hecho.log)
    --pid-path=PIDPATH  pidfile path (default: ~/.hecho/hecho.pid)
    --foreground        run in foreground mode (default: disabled)
    --disable-log       disable logging (default: disabled)


Running
=======

Starting the server::

    $ hecho start

Verify log, process and tcp listen address::

    $ tail ~/.hecho/hecho.log
    [28/Dec/2018 16:23:10] Starting server...

    $  ps aux | grep hecho
    myuser  23648  0.0  1.5 214444 15720 ?  S  15:54  0:00 python hecho.py start

    $ netstat -nlp | grep python
    tcp  0  0 127.0.0.1:8000  0.0.0.0:*  LISTEN  23648/python

Simple test::

    $ curl localhost:8000

    {
        "headers": {
            "ACCEPT": "*/*",
            "HOST": "localhost:8000",
            "USER-AGENT": "curl/7.19.7 (x86_64-redhat-linux-gnu) libcurl/7.19.7 NSS/3.27.1 zlib/1.2.3 libidn/1.18 libssh2/1.4.2"
        },
        "method": "GET",
        "origin": "127.0.0.1",
        "params": {},
        "url": "http://localhost:8000/"
    }

Verify log::

    $ tail ~/.hecho/hecho.log
    [28/Dec/2018 16:23:10] Starting server...
    [28/Dec/2018 16:24:55] 127.0.0.1 GET http://localhost:8000/ 200 313 curl/7.19.7 (x86_64-redhat-linux-gnu) libcurl/7.19.7 NSS/3.27.1 zlib/1.2.3 libidn/1.18 libssh2/1.4.2

Stopping the server::

    $ hecho stop


.. _Falcon: https://github.com/falconry/falcon
.. _Bjoern: https://github.com/jonashaag/bjoern


.. |Downloads| image:: https://pepy.tech/badge/hecho
