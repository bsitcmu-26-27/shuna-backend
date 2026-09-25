from bottle import route, run, request, ServerAdapter

class ShunaServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

        class RequestHandler(WSGIRequestHandler):
            def handle(self):
                super().handle()

            def address_string(self):
                xff = self.headers.get('X-Forwarded-For')
                if xff:
                    return [ip.strip() for ip in xff.split(',')][-1]
                return super().address_string()

        self.options['handler_class'] = RequestHandler
        srv = WSGIServer((self.host, self.port), RequestHandler)
        srv.set_app(handler)
        srv.serve_forever()

