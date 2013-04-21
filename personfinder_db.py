import txmongo
import cyclone.web
from twisted.internet import defer
from twisted.application import service, internet
from cyclone.httpclient import fetch

class IndexHandler(cyclone.web.RequestHandler):
    @defer.inlineCallbacks
    def get(self):
        name = self.get_argument("name")
        try:
            result = yield self.settings.db.find({"name":name})
        except Exception, e:
            self.write("find failed: %s\n" % str(e))
        else:
            self.write("result(s): %s\n" % repr(result))
        self.finish()

    def post(self):
        name = self.get_argument("name")
        self.settings.db.insert({"name":name})
        self.write("ok\n")

class PersonFinderDB(cyclone.web.Application):
    def __init__(self):
        handlers = [
            (r"/",       IndexHandler),
        ]

        mongo = txmongo.lazyMongoConnectionPool()
        settings = {
            "db": mongo.foo.test
            #"static_path": "./static",
        }

        cyclone.web.Application.__init__(self, handlers, **settings)


application = service.Application("PersonFinderDB")
port = int(os.environ.get('PORT', 5000))
srv = internet.TCPServer(port, PersonFinderDB(), interface="127.0.0.1")
srv.setServiceParent(application)