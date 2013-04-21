import os, sys
import txmongo
import pymongo.uri_parser
import cyclone.web
from twisted.python import log
from twisted.internet import defer, reactor
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

        mongo_uri = os.environ.get(
            "MONGOLAB_URI", 
            "mongodb://db_admin:personfinder@ds041347.mongolab.com/heroku_app15142536")
        mongo_creds = pymongo.uri_parser.parse_uri(mongo_uri)

        conn = txmongo.lazyMongoConnectionPool(
            *mongo_creds['nodelist'][0], 
            pool_size=5)

        mongo = getattr(conn, mongo_creds['database'])
        mongo.authenticate(
                mongo_creds['username'], 
                mongo_creds['password'])

        settings = {
            "mongo": mongo,
            "db": mongo.people
            #"static_path": "./static",
        }

        cyclone.web.Application.__init__(self, handlers, **settings)

log.startLogging(sys.stdout)
port = int(os.environ.get('PORT', 5000))
reactor.listenTCP(port, PersonFinderDB())
reactor.run()