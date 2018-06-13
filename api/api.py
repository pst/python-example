import json
import os

import tornado.gen
import tornado.ioloop
import tornado.netutil
import tornado.web
from tornado.options import define, options

define("port", default="5555", help="Port to listen on")
define("debug", default=False, help="Enable debug mode")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/v1(?:/([a-z_]*))?', ApiHandler),
            (r'/healthz', HealthzHandler)]

        tornado.web.Application.__init__(
            self, handlers, debug=options.debug)


class PeerMixin(object):
    @tornado.gen.coroutine
    def get_peers(self):
        dns = tornado.netutil.Resolver()
        response = yield dns.resolve('www.coreos.com', 8001)
        for entry in response:
            family, address = entry
            # if family == 2:
            #     print(type(family), address)
        return response


class ApiHandler(tornado.web.RequestHandler, PeerMixin):
    @tornado.gen.coroutine
    def get(self, slug):
        hostname = os.environ.get('HOSTNAME', None)
        if not hostname:
            raise tornado.web.HTTPError(500)

        peers = yield self.get_peers()
        response = {'hostname': f'{hostname}',
                    'peers': peers}

        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.write(json.dumps(response))


class HealthzHandler(tornado.web.RequestHandler):
    def get(self):
        hostname = os.environ.get('HOSTNAME', None)
        if not hostname:
            raise tornado.web.HTTPError(500)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()

    if options.debug:
        # debug mode
        app.listen(options.port)
        tornado.ioloop.IOLoop.current().start()
    else:
        # prod mode
        server = tornado.httpserver.HTTPServer(app, xheaders=True)
        server.bind(options.port)
        try:
            server.start(0)  # 0 autodetects cores and forks one process each
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            tornado.ioloop.IOLoop.instance().stop()
