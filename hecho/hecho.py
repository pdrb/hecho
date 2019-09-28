#!/usr/bin/env python

# hecho 0.1.4
# author: Pedro Buteri Gonring
# email: pedro@bigode.net
# date: 20190928

import optparse
import os
import logging
import datetime
import sys
import json

from .daemon import Daemon

import falcon
import bjoern


_version = '0.1.4'


# Class used to daemonize the process
class HechoDaemon(Daemon):
    def run(self):
        init()


# Handler for simple post 'x-www-form-urlencoded' requests
class FormHandler(object):
    def deserialize(self, raw):
        return raw.decode()


# Log all requests
class LoggingMiddleware(object):
    def process_response(self, req, resp, resource, req_succeeded):
        date = datetime.datetime.now().strftime('[%d/%b/%Y %H:%M:%S]')
        status = resp.status.split(' ')[0]
        try:
            length = len(resp.body)
        except:
            length = 0
        user_agent = req.get_header('user-agent', default='')
        real_ip = req.get_header('x-real-ip', default='')
        if real_ip == '':
            real_ip = req.remote_addr
        logger.info('%s %s %s %s %s %s %s' % (date, real_ip, req.method,
                    req.url, status, length, user_agent))


# Falcon resource
class RootResource(object):
    def create_response(self, req):
        response = {}
        response['headers'] = req.headers
        response['params'] = req.params
        response['url'] = req.url
        response['method'] = req.method
        response['origin'] = self.get_real_ip(req, response)
        return response

    def get_real_ip(self, req, response):
        real_ip = req.get_header('x-real-ip', default='')
        if real_ip == '':
            real_ip = req.remote_addr
        else:
            del(response['headers']['X-REAL-IP'])
        return real_ip

    def on_get(self, req, resp):
        response = self.create_response(req)
        # Prettify the json response
        resp.body = json.dumps(response, indent=4, sort_keys=True)

    def on_post(self, req, resp):
        response = self.create_response(req)
        if req.content_length == 0:
            response['json'] = None
        else:
            response['json'] = req.media
        resp.body = json.dumps(response, indent=4, sort_keys=True)

    def on_put(self, req, resp):
        self.on_post(req, resp)

    def on_patch(self, req, resp):
        self.on_post(req, resp)

    def on_delete(self, req, resp):
        self.on_post(req, resp)


# Parse and validate arguments
def get_parsed_args():
    usage = 'usage: %prog [options] start|stop|restart'
    # Configure the default paths
    home_dir = os.path.expanduser('~')
    hecho_dir = os.path.join(home_dir, '.hecho')
    logfile = os.path.join(hecho_dir, 'hecho.log')
    pidfile = os.path.join(hecho_dir, 'hecho.pid')
    # Create the parser
    parser = optparse.OptionParser(
        description='simple and fast http echo server',
        usage=usage, version=_version, add_help_option=True
    )
    parser.add_option(
        '-l', dest='address', default='localhost',
        help='address to listen (default: %default)'
    )
    parser.add_option(
        '-p', dest='port', default=8000, type=int,
        help='application port (default: %default)'
    )
    parser.add_option(
        '--log-path', dest='logpath', default=logfile,
        help='logfile path (default: %default)'
    )
    parser.add_option(
        '--pid-path', dest='pidpath', default=pidfile,
        help='pidfile path (default: %default)'
    )
    parser.add_option(
        '--foreground', action='store_true', default=False,
        help='run in foreground mode (default: disabled)'
    )
    parser.add_option(
        '--disable-log', action='store_true', default=False,
        help='disable logging (default: disabled)'
    )

    # Print help if no argument is given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    # Parse the args
    (options, args) = parser.parse_args()

    # Some args validation
    if len(args) == 0:
        parser.error('missing command, use: start|stop|restart')
    if len(args) > 1:
        parser.error('too many arguments')
    if not 1 <= options.port <= 65535:
        parser.error('invalid port, port range is 1-65535')

    # Create the dirs if needed
    logdir = os.path.split(options.logpath)[0]
    piddir = os.path.split(options.pidpath)[0]
    if not os.path.exists(logdir):
        make_dir(logdir)
    if not os.path.exists(piddir):
        make_dir(piddir)
    # Check for write permission
    check_write_perm(options.logpath)
    check_write_perm(options.pidpath)
    # Remove the pidfile if it is empty
    with open(options.pidpath) as f:
        if f.read() == '':
            os.remove(options.pidpath)
    return (options, args)


# Create directory
def make_dir(path):
    try:
        os.makedirs(path)
    except Exception as ex:
        print('\nError creating directory: %s\n' % ex)
        sys.exit(1)


# Check for write permission
def check_write_perm(path):
    try:
        f = open(path, 'a+')
    except Exception as ex:
        print('\nWrite permission error: %s\n' % ex)
        sys.exit(1)
    f.close()


# Custom 404 handler
def handle_404(req, resp):
    resp.content_type = falcon.MEDIA_HTML
    resp.status = falcon.HTTP_404
    resp.body = '<html><title>404 Not Found</title><h1>404 NOT FOUND</h1>' + \
                '<p>The requested URL was not found on the server.</p></html>'


def main():
    global options
    global logger
    global init_date

    (options, args) = get_parsed_args()
    command = args[0].lower()
    if command not in ('start', 'stop', 'restart'):
        print('\nError: Invalid command "%s"\n' % command)
        sys.exit(1)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(options.logpath)
    logger.addHandler(file_handler)

    init_date = datetime.datetime.now().strftime('[%d/%b/%Y %H:%M:%S]')
    if options.foreground:
        # Add stdout to logger
        std_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(std_handler)
        init()
    else:
        daemon = HechoDaemon(options.pidpath)
        if command == 'start':
            logger.info('%s Starting server...' % init_date)
            daemon.start()
        elif command == 'stop':
            logger.info('%s Stopping server...' % init_date)
            daemon.stop()
        elif command == 'restart':
            logger.info('%s Restarting server...' % init_date)
            daemon.restart()


# Daemon entry point
def init():
    extra_handlers = {
        'application/x-www-form-urlencoded': FormHandler()
    }

    if options.disable_log:
        app = falcon.API()
    else:
        app = falcon.API(middleware=[LoggingMiddleware()])

    # Enable parsing of urlencoded post requests and register the handler
    app.req_options.auto_parse_form_urlencoded = True
    app.req_options.media_handlers.update(extra_handlers)

    # Create root route and register custom 404 handler
    app.add_route('/', RootResource())
    app.add_sink(handle_404, '')

    try:
        bjoern.run(app, options.address, options.port)
    except Exception as ex:
        logger.critical(
            '%s Error starting server on "%s:%s": %s' % (
                init_date, options.address, options.port, ex
            )
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
