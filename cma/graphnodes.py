
#!/usr/bin/env python
# vim: smartindent tabstop=4 shiftwidth=4 expandtab number
#
# This file is part of the Assimilation Project.
#
# Copyright (C) 2011, 2012 - Alan Robertson <alanr@unix.sh>
#
#  The Assimilation software is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  The Assimilation software is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with the Assimilation Project software.  If not, see http://www.gnu.org/licenses/
#
#
from consts import CMAconsts
from store import Store
from os import path
from hashlib import md5
import sys, re
from AssimCtypes import ADDR_FAMILY_IPV4, ADDR_FAMILY_IPV6
from AssimCclasses import pyNetAddr
'''
This module defines the classes for all our CMA nodes ...
'''

def nodeconstructor(**properties):
    'A class-like constructor that knows our class name is stored as nodetype'
    realcls = eval(properties['nodetype'])
    return Store._callconstructor(realcls, properties)

class CMAclass(object):
    '''Class defining the relationships of our CMA classes to each other'''

    def __init__(self, name):
        self.name = name
        self.domain = CMAconsts.globaldomain
        self.nodetype = CMAconsts.NODE_nodetype
        assert str(self.name) == str(name)

    def __str__(self):
        'Default routine for printing CMAclass objects'
        result = '%s({' % self.__class__.__name__
        comma  = ''
        for attr in Store._safe_attrs(self):
            result += '%s%s = %s'% (comma, attr, str(getattr(self, attr)))
            comma = ",\n    "
        if Store.has_node(self):
            if Store.is_abstract(self):
                result += comma + 'HasNode = "abstract"'
            else:
                result += (comma + 'HasNode = %d' %Store.id(self))

        result += "\n})"
        return result


class GraphNode(object):
    REESC=re.compile(r'\\')
    REQUOTE=re.compile(r'"')

    def __init__(self, domain, roles=[]):
        'Abstract Graph node base class'
        self.domain = domain
        self.nodetype = self.__class__.__name__
        self._baseinitfinished=False
        if roles == []:
            # Neo4j can't initialize node properties to empty arrays because
            # it wants to know what kind of array it is...
            roles = ['']
        self.roles = roles

    def addrole(self, roles):
        if len(self.roles) > 0 and self.roles[0] == '':
            self.delrole('')
        if isinstance(roles, tuple) or isinstance(roles, list):
            for role in roles:
                self.addrole(role)
            return self.roles
        assert isinstance(roles, str) or isinstance(roles, unicode)
        if self.roles is None:
            self.roles=[roles]
        elif not roles in self.roles:
            self.roles.append(roles)
        return self.roles

    def delrole(self, roles):
        if isinstance(roles, tuple) or isinstance(roles, list):
            for role in roles:
                self.delrole(role)
            return self.roles
        assert isinstance(roles, str) or isinstance(roles, unicode)
        if roles in self.roles:
            self.roles.remove(roles)
        return self.roles


    def post_db_init(self):
        '''Create IS_A relationship to our 'class' node in the database'''
        if not self._baseinitfinished:
            self._baseinitfinished = True
            if Store.is_abstract(self):
                Store.getstore(self).relate(self, CMAconsts.REL_isa
                ,   CMAconsts.classtypeobjs[self.nodetype])

    def update_attributes(self, other):
        'Update our attributes from another node of the same type'
        if other.nodetype != self.nodetype:
            raise ValueError('Cannot update attributes from incompatible nodes (%s vs %s)'
            %   (self.nodetype, other.nodetype))
        for attr in other.__dict__.keys():
            if not hasattr(self, attr) or getattr(self, attr) != getattr(other, attr):
                self.attr = other.attr
        return self

    def __str__(self):
        'Default routine for printing GraphNodes'
        result = '%s({' % self.__class__.__name__
        comma  = ''
        for attr in Store._safe_attrs(self):
            result += '%s%s = %s'% (comma, attr, str(getattr(self, attr)))
            comma = ",\n    "
        if Store.has_node(self):
            if Store.is_abstract(self):
                result += comma + 'HasNode = "abstract"'
            else:
                result += (comma + 'HasNode = %d' %Store.id(self))

        result += "\n})"
        return result

    def JSON(self, includemap=None, excludemap=None):
        '''Output this object according to JSON rules. We take advantage
        of the fact that Neo4j restricts what kind of objects we can
        have as Node properties.
        '''

        attrstodump = []
        for attr in Store._safe_attrs(self):
            if includemap is not None and attr not in includemap:
                continue
            if excludemap is not None and attr in excludemap:
                continue
            attrstodump.append(attr)
        ret = '{'
        comma=''
        for attr in attrstodump.sort():
            ret += '%s"%s": %s' % (comma, attr, GraphNode._JSONelem(getattr(self, attr)))
            comma = ','
        ret += '}'
        return ret

    @staticmethod
    def _JSONelem(value):
        'Return the value of an element suitable for JSON output'
        if isinstance(value, str) or isinstance(value, unicode):
            return '"%s"' % GraphNode._JSONesc(value)
        if isinstance(value, bool):
            if value:
                return 'true'
            return 'false'
        if isinstance(value, list) or isinstance(value, tuple):
            ret = '['
            comma = ''
            for elem in value:
                ret += '%s%s' % (comma, GraphNode._JSONelem(elem))
                comma=','
            ret += ']'
            return ret
        return str(value)

    @staticmethod
    def _JSONesc(stringthing):
        'Escape this string according to JSON string escaping rules'
        stringthing = GraphNode.REESC.sub(r'\\\\', stringthing)
        stringthing = GraphNode.REQUOTE.sub(r'\"', stringthing)
        return stringthing

    @staticmethod
    def dump_nodes(nodetype='Drone', stream=sys.stderr):
        'Dump all our drones out to the given stream (defaults to sys.stderr)'
        idx = CMAconsts.classindextable[nodetype]
        query= '*:*'
        #print >> stream, 'QUERY against %s IS: "%s"' % (idx, query)
        dronelist = idx.query(query)
        dronelist = [drone for drone in dronelist]
        print >> stream, 'List of %ss: %s' % (nodetype, dronelist)
        for drone in dronelist:
            print >> stream, ('NODE %s (%s id=%s)' % (nodetype
            ,   str(drone.get_properties()), drone._id))
            for rel in drone.match():
                start=rel.start_node
                end=rel.end_node
                if start._id == drone._id:
                    print >> stream, '    (%s)-[%s]->(%s:%s,%s)' \
                    %       (drone['designation'], rel.type, end['nodetype'], end['designation'], end._id)
                else:
                    print >> stream, '    (%s:%s,%s)-[%s]->(%s)' \
                    %       (start['designation'], start['nodetype'], start._id, rel.type, drone['designation'])
                if start._id == end._id:
                    print >> stream, 'SELF-REFERENCE to %s' % start._id

class SystemNode(GraphNode):
    'An object that represents a physical or virtual system (server, switch, etc)'
    # We really ought to figure out how to make Drone a subclass of SystemNode
    def __init__(self, domain, name, roles=[]):
        GraphNode.__init__(self, domain=domain, roles=roles)
        self.name=name

class NICNode(GraphNode):
    'An object that represents a NIC - characterized by its MAC address'
    def __init__(self, domain, macaddr, ifname='unknown'):
        GraphNode.__init__(self, domain=domain)
        self.macaddr=macaddr
        self.ifname=ifname

class IPaddrNode(GraphNode):
    '''An object that represents a v4 or v6 IP address without a port - characterized by its IP address
    They are always represented in the database in ipv6 format without a port
    '''
    def __init__(self, domain, ipaddr, cidrmask='unknown'):
        'Construct an IPaddrNode - validating our parameters'
        GraphNode.__init__(self, domain=domain)
        if isinstance(ipaddr, str) or isinstance(ipaddr, unicode):
            ipaddr = pyNetAddr(str(ipaddr))
        if isinstance(ipaddr, pyNetAddr):
            addrtype = ipaddr.addrtype()
            if addrtype == ADDR_FAMILY_IPV4:
                ipaddr = ipaddr.toIPv6()
            elif addrtype != ADDR_FAMILY_IPV6:
                raise ValueError('Invalid network address type for IPaddrNode constructor: %s'
                %   str(ipaddr))
            ipaddr.setport(0)
            ipaddr = unicode(str(ipaddr))
        else:
            raise ValueError('Invalid address type for IPaddrNode constructor: %s type(%s)'
            %   (str(ipaddr), type(ipaddr)))
        self.ipaddr=ipaddr
        self.cidrmask=cidrmask
        
class IPtcpportNode(GraphNode):
    'An object that represents an IP:port combination characterized by the pair'
    def __init__(self, domain, ipaddr, port=None, protocol='tcp'):
        'Construct an IPtcpportNode - validating our parameters'
        GraphNode.__init__(self, domain=domain)
        if isinstance(ipaddr, str) or isinstance(ipaddr, unicode):
            ipaddr = pyNetAddr(str(ipaddr))
        if isinstance(ipaddr, pyNetAddr):
            if port is None:
                port = ipaddr.port()
            if port <= 0 or port >= 65536:
                raise ValueError('Invalid port for constructor: %s' % str(port))
            addrtype = ipaddr.addrtype()
            if addrtype == ADDR_FAMILY_IPV4:
                ipaddr = ipaddr.toIPv6()
            elif addrtype != ADDR_FAMILY_IPV6:
                raise ValueError('Invalid network address type [%s] for constructor: %s'
                %  (addrtype, str(ipaddr)))
            ipaddr.setport(0)
            ipaddr = unicode(str(ipaddr))
        else:
            raise ValueError('Invalid address type for constructor: %s type(%s)'
            %   (str(ipaddr), type(ipaddr)))
        self.ipaddr=ipaddr
        self.port=port
        self.protocol='tcp'
        self.ipport = self.format_ipport()

    def format_ipport(self, ipaddr, port):
        '''Format the ip and port into our key field
        Note that we make the port the most significant part of the key - which
        should allow some more interesting queries.
        '''
        return '%s_%s_%s' % (self.port, self.protocol, self.ipaddr)
        

class ProcessNode(GraphNode):
    def __init__(self, domain, host, pathname, arglist, uid, gid, cwd, roles=[]):
        GraphNode.__init__(self, domain=domain, roles=roles)
        self.host=host
        self.pathname=pathname
        self.arglist=arglist
        self.uid=uid
        self.gid=gid
        self.cwd=cwd
        #self.processname='%s|%s|%s|%s:%s|%s' \
        #%       (path.basename(pathname), path.dirname(pathname), host, uid, gid, str(arglist))
        sum=md5()
        procstring='%s|%s|%s:%s|%s' \
        %       (path.dirname(pathname), host, uid, gid, str(arglist))
        sum.update(procstring)
        self.processname='%s_%s' % (path.basename(pathname), sum.hexdigest())

if __name__ == '__main__':
    print >> sys.stderr, 'Starting'
    CMAinit(None, cleanoutdb=True, debug=True)
    if Store.getstore(self).transaction_pending:
        print 'Transaction pending in:', Store.getstore(self)
        print 'Results:', Store.getstore(self).commit()
    print >> sys.stderr, 'Init done'
