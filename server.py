import cjson
from twisted.internet import reactor

from twisted.internet.protocol import DatagramProtocol



class UServer(DatagramProtocol):

    def __init__(self):
        self.clients = {}
        

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        who = (host, port)
        try:
            msg = cjson.decode(data)
            t = msg['type']
            if t == 'register':
                print 'Register %r %r'%(msg, who)
                self.clients[msg['name']] = (host, port)
                self.transport.write(cjson.encode({'type': 'registered'}), who)
            elif t == 'list':
                self.handle_list(who)
        except Exception, e:
            print 'E: %r'%e

    def handle_list(self, who):
        self.transport.write(cjson.encode({'type': 'list',
                                           'clients': self.clients}), who)


def main():
    reactor.listenUDP(2322, UServer())
    reactor.run()

if __name__ == '__main__':
    main()
