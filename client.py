import cjson
import sys
from twisted.internet import reactor

from twisted.internet.protocol import DatagramProtocol


class UClient(DatagramProtocol):
    def __init__(self, name, host, port=2322):
        self.name = name
        self.host = host
        self.port = port
        self.who = (self.host, self.port)
        self.registered = False
        self.tunnel = None

    def startProtocol(self):
        reactor.callLater(2, self.run_loop)

    def run_loop(self):
        if not self.registered:
            print 'Try to register'
            self.transport.write(cjson.encode({'type': 'register',
                                               'name': self.name,
                                           }), self.who)
        elif not self.tunnel:
            self.transport.write(cjson.encode({'type': 'list'}), self.who)
        else:
            self.transport.write(cjson.encode({'type': 'tunnel'}), self.tunnel)
        reactor.callLater(2, self.run_loop)

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        who = (host, port)
        try:
            msg = cjson.decode(data)
            t = msg['type']
            if t == 'registered':
                self.handle_registered(who)
            elif t == 'list':
                self.handle_clients(msg, who)
            elif t == 'tunnel':
                self.handle_tunnel(msg, who)
        except Exception, e:
            print 'E: %r'%e

    def handle_registered(self, who):
        self.registered = True
        print 'Registered ok'

    def handle_clients(self, msg, who):
        print 'Got clients %r'%msg
        for name, w in msg['clients'].iteritems():
            if self.name != name:
                self.transport.write(cjson.encode({'type':'tunnel'}), (w[0], w[1]))

    def handle_tunnel(self, msg, who):
        if who == self.tunnel:
            print 'Got tunnel ping message from %r'%(who,)
        else:
            print 'Got tunnel message %r'%((who,))
            self.tunnel = who


def main():
    reactor.listenUDP(2321, UClient(sys.argv[1], sys.argv[2]))
    reactor.run()

if __name__ == '__main__':
    main()
