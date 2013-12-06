#!/usr/bin/env python
# vim: smartindent tabstop=4 shiftwidth=4 expandtab number
#
# This file is part of the Assimilation Project.
#
# Copyright (C) 2013 Assimilation Systems Limited - author Alan Robertson <alanr@unix.sh>
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
'''
This file implements Monitoring-related classes.

MonitorAction is a class that represents currently active monitoring actions.

MonitoringRule and its subclasses implement the logic to automatically create monitoring
rules for certain kinds of services automatically.
'''


from AssimCtypes import REQCLASSNAMEFIELD, REQTYPENAMEFIELD, REQPROVIDERNAMEFIELD        \
,   REQENVIRONNAMEFIELD, REQRSCNAMEFIELD, REQREPEATNAMEFIELD, REQTIMEOUTNAMEFIELD
from AssimCclasses import pyConfigContext
from frameinfo import FrameTypes, FrameSetTypes
from graphnodes import GraphNode, RegisterGraphClass
from droneinfo import Drone
from cmadb import CMAdb
from consts import CMAconsts
import re
#
#
@RegisterGraphClass
class MonitorAction(GraphNode):
    '''Class representing monitoring actions
    '''
    @staticmethod
    def __meta_keyattrs__():
        'Return our key attributes in order of significance (sort order)'
        return ['monitorname', 'domain']


    # R0913: too many arguments
    # pylint: disable=R0913
    def __init__(self, domain, monitorname, monitorclass, monitortype, interval
    ,   timeout, provider=None, arglist=None):
        'Create the requested monitoring rule object.'
        GraphNode.__init__(self, domain)
        self.monitorname = monitorname
        self.monitorclass = monitorclass
        self.monitortype = monitortype
        self.interval = interval
        self.timeout = timeout
        self.provider = provider
        self.arglist = arglist
        self.isactive = False

    def activate(self, monitoredentity, runon=None):
        '''Relate this monitoring action to the given entity, and start it on the 'runon' system
          Parameters
          ----------
          monitoredentity : GraphNode
                The graph node which we are monitoring
          runon : Drone
                The particular Drone which is running this monitoring action.
                Defaults to 'monitoredentity'
        '''
        if runon is None:
            runon = monitoredentity
        assert isinstance(monitoredentity, GraphNode)
        assert isinstance(runon, Drone)
        CMAdb.store.relate_new(self, CMAconsts.REL_monitoring, monitoredentity)
        CMAdb.store.relate_new(runon, CMAconsts.REL_hosting, self)
        reqjson = self.construct_mon_json()
        CMAdb.transaction.add_packet(runon.primary_ip(), FrameSetTypes.DORSCOP, reqjson
        ,   frametype=FrameTypes.RSCJSON)
        self.isactive = True
        
    def deactivate(self):
        '''Deactivate this monitoring action. Does not remove relationships from the graph'''
        reqjson = self.construct_mon_json()
        for drone in CMAdb.store.load_related(self, CMAconsts.REL_hosting, Drone):
            CMAdb.transaction.add_packet(drone.primary_ip(), FrameSetTypes.STOPRSCOP
            ,   reqjson, frametype=FrameTypes.RSCJSON)
        self.isactive = False

    def construct_mon_json(self):
        '''
          Parameters
          ----------
          Returns
          ----------
          JSON string representing this particular monitor action.
          '''
        if self.arglist is None:
            arglist_str = ''
        else:
            arglist_str = ', "%s": [' % (REQENVIRONNAMEFIELD)
            comma = ''
            for arg in self.arglist:
                arglist_str += '%s"%s"' % (comma, str(arg))
                comma = ','
            arglist_str += ']'

        if self.provider is None:
            provider_str = ''
        else:
            provider_str = ', "%s":"%s"' % (REQPROVIDERNAMEFIELD, self.provider)

        json = '{"%s":"%s", "%s":"%s", "%s":"%s", "%s":%d, "%s":%d%s%s}' % \
        (   REQCLASSNAMEFIELD, self.monitorclass
        ,   REQTYPENAMEFIELD, self.monitortype
        ,   REQRSCNAMEFIELD, self.monitorname
        ,   REQREPEATNAMEFIELD, self.interval
        ,   REQTIMEOUTNAMEFIELD, self.timeout
        ,   provider_str, arglist_str)
        return str(pyConfigContext(init=json))


class MonitoringRule:
    '''Abstract base class for implementing monitoring rules

    This particular class implements it for simple regex matching on arbitrary regexes
    on fields on ProcessNodes or Drones -- in reality on any set of graph nodes.

    The question is how many subclasses should there be?  It's obvious that we need to have
    specialized subclasses for Java, Python and other interpreted languages.
    What comes to mind to implement first is simple monitoring using LSB scripts.

    The reason for doing this is that they don't take any parameters, so all you have to do
    is match the pattern and then know what init script name is used for that service on that OS.

    It does vary by Linux distribution, for example...
    So... (cmd-pattern, arg-pattern, OS-pattern, distro-pattern) see to be the things that
    uniquely determine what init script to use to monitor that particular resource type.

    The second question that comes to mind is how to connect these rules into a rule
    hierarchy.

    For example, if the command name matches Java, then invoke the java rules.

    If a java rule matches Neo4j, then return the Neo4j monitoring action
        and so on...

    Note that for Java, the monitoring rule is likely to match the _last_ argument
        in the argument string...
            arg[-1] - python-style

    If it matches python, then match it against the second argument (arg[1])

    '''
    NOMATCH = 0
    PARTMATCH = 2
    LOWPRIOMATCH = 2
    HIGHPRIOMATCH = 3

    functions = {}

    def __init__(self, tuplespec):
        '''It is constructed from an list of tuples, each one of which represents
        a value expression and a regular expression.  Each value expression
        is a specification to a GraphNode 'get' operation.  Each regular expression
        is a specification of a regex to match against the corresponding field
        expression.  By default, all regexes are anchored (implicitly start with ^)
        This rule can only apply if all the RegExes match.
        NOTE: It can still fail to apply even if the RegExes all match.
        '''
        if tuplespec is None or len(tuplespec) == 0:
            raise ValueError('Improper tuplespec')

        self._tuplespec = []
        for tup in tuplespec:
            if len(tup) < 2 or len(tup) > 3:
                raise ValueError('Improperly formed constructor argument')
            try:
                if len(tup) == 3:
                    flags = tup[2]
                    regex = re.compile(tup[1], flags)
                else:
                    regex = re.compile(tup[1])
            except:
                raise ValueError('Improperly formed regular expression')
            self._tuplespec.append((tup[0], regex))


    def specmatch(self, graphnodes):
        '''Return a MonitorAction if this rule can be applies to this particular set of GraphNodes
        Note that the GraphNodes that we're given at the present time are typically expected to be
        the Drone node for the node it's running on and the Process node for the process
        to be monitored.
        We return (MonitoringRule.NOMATCH, None) on no match
        '''
        values = {}
        for tup in self._tuplespec:
            expression = tup[0]
            value = MonitoringRule.evaluate(expression, values, graphnodes)
            if value is None:
                return (MonitoringRule.NOMATCH, None)
        # We now have a complete set of values to match against our regexes...
        for tup in self._tuplespec:
            name = tup[0]
            regex = tup[1]
            val = values[name]
            if not isinstance(val, (str, unicode)):
                val = str(val)
            if not regex.match(val):
                return (MonitoringRule.NOMATCH, None)
        # We now have a matching set of values to give our monitoring constructor
        return self.constructaction(values, graphnodes)

    @staticmethod
    def evaluate(expression, values, graphnodes):
        '''
        Evaluate an expression.
        It can be:
            None - return None
            'some-value -- return some-value (it's a constant)
            or an expression to find in values or graphnodes
            or @functionname(args) - for defined functions...

            We may add other kinds of expressions in the future...
        '''
        if expression is None:
            return None
        if expression.startswith("'"):
            # The value of this parameter is a constant...
            return expression[1:]
        if expression.startswith('@'):
            value = MonitoringRule.functioncall(expression[1:], values, graphnodes)
            values[expression] = value
        if expression in values:
            return values[expression]
        for node in graphnodes:
            value = node.get(expression)
            if value is not None:
                values[expression] = value
                return value
        return None

    @staticmethod
    def functioncall(expression, values, graphnodes):
        '''Performs a function call for our expression language

        Figures out the function name, and the arguments and then
        calls that function with those arguments.

        All our defined functions take an argv argument string first, then the values
        and graphnodes arguments.

        '''
        expression = expression.strip()
        if expression[-1] != ')':
            return None
        expression = expression[:len(expression)-1]
        (funname, arglist) = expression.split('(', 1)
        funname = funname.strip()
        arglist = arglist.strip()
        argsin = arglist.split(',')
        args = []
        for arg in argsin:
            args.append(arg.strip())
        if funname not in MonitoringRule.functions:
            return None
        return MonitoringRule.functions[funname](args, values, graphnodes)

    @staticmethod
    def RegisterFun(function):
        'Function to register other functions as built-in MonitoringRule functions'
        MonitoringRule.functions[function.__name__] = function

    def constructaction(self, values, graphnodes):
        '''Return a tuple consisting of a tuple as noted:
            (MonitoringRule.PRIORITYVALUE, MonitorActionArgs, optional-information)
        If PRIORITYVALUE is NOMATCH, the MonitorAction will be None -- and vice versa

        If PRIORITYVALUE IS PARTMATCH, then more information is needed to determine
        exactly how to monitor it.  In this case, the optional-information element
        will be present and is a list the names of the fields whose values have to
        be supplied in order to monitor this service/host/resource.

        If PRIORITYVALUE is LOWPRIOMATCH or HIGHPRIOMATCH, then there is no optional-information
        element in the tuple.

        A LOWPRIOMATCH method of monitoring is presumed to do a minimal form of monitoring.
        A HIGHPRIOMATCH method of monitoring is presumed to do a more complete job of
        monitoring - presumably acceptable, and preferred over a LOWPRIOMATCH.

        MonitorActionArgs is a hash table giving the values of the various arguments
        that you need to give to the MonitorAction constuctor.  It will always supply
        the values of the monitorclass and monitortype argument.  If needed, it will
        also supply the values of the provider and arglist arguments.

        If PRIORITYVALUE is PARTMATCH, then it will supply an incomplete 'arglist' value.
        and optional-information list consists of a list of those arguments whose values
        cannot be determined automatically from the given value set.

        The caller still needs to come up with these arguments for the MonitorAction constructor
            monitorname - a unique name for this monitoring action
            interval - how often to run this monitoring action
            timeout - what timeout to use before declaring monitoring failure

        Not that the implementation in the base class does nothing, and will result in
        raising a NotImplementedError exception.
        '''
        raise NotImplementedError('Abstract class')

class LSBMonitoringRule(MonitoringRule):

    '''Class for implementing monitoring rules for sucky LSB style init script monitoring
    '''
    def __init__(self, servicename, tuplespec):
        self.servicename = servicename
        MonitoringRule.__init__(self, tuplespec)

    def constructaction(self, values, graphnodes):
        '''Construct arguments
        '''
        return (MonitoringRule.LOWPRIOMATCH
        ,       {   'monitorclass': 'lsb'
                ,   'monitortype':  self.servicename
                ,   'provider':     None
                ,   'arglist':      None}
        )

#
# abstract class only referenced once
# pylint: disable=R0922,R0922
class OCFMonitoringRule(MonitoringRule):
    '''Class for implementing monitoring rules for OCF style init script monitoring
    OCF ==  Open Cluster Framework
    '''
    def __init__(self, provider, rsctype, triplespec):
        '''
        Parameters
        ----------
        provider: str
            The OCF provider name for this resource
            This is the directory name this resource is found in
        rsctype: str
            The OCF resource type for this resource (service)
            This is the same as the script name for the resource

        triplespec: list
            Similar to but wider than the MonitoringRule tuplespec
            (name,  expression, regex,  regexflags(optional))

            'name' is the name of an OCF RA parameter or None or '-'
            'expression' is an expression for computing the value for that name
            'regex' is a regular expression that the value of 'expression' has to match
            'regexflags' is the optional re flages for 'regex'

            If there is no name to go with the tuple, then the name is given as None or '-'
            If there is no regular expression to go with the name, then the expression
                and remaining tuple elements are missing.  This can happen if there
                is no mechanical way to determine this value from discovery information.
            If there is a name and expression but no regex, the regex is assumed to be '.'
        '''
        self.provider = provider
        self.rsctype = rsctype
        self.nvpairs = {}
        tuplespec = []

        for tup in triplespec:
            tuplen = len(tup)
            if tuplen == 4:
                (name, expression, regex, flags) = tup
                tuplespec.append((expression, regex, flags))
            elif tuplen == 3:
                (name, expression, regex) = tup
                tuplespec.append((expression, regex))
            elif tuplen == 2:
                (name, expression) = tup
            elif tuplen == 1:
                name = tup[0]
                expression = None
            else:
                raise ValueError('Invalid tuple length (%d)' % tuplen)
            if name is not None and name != '-':
                self.nvpairs[name] = expression
        MonitoringRule.__init__(self, tuplespec)


    def constructaction(self, values, graphnodes):
        '''Construct arguments to give MonitorAction constructor
            We can either return a complete match (HIGHPRIOMATCH)
            or an incomplete match (PARTMATCH) if we can't find
            all the parameter values in the nodes we're given
        '''
        #
        missinglist = []
        arglist = {}
        # Figure out what we know how to supply and what we need to ask
        # a human for -- in order to properly monitor this resource
        for name in self.nvpairs:
            expression = self.nvpairs[name]
            val = MonitoringRule.evaluate(expression, values, graphnodes)
            if val is None:
                missinglist.append(name)
            else:
                arglist[name] = str(val)
        if len(missinglist) == 0:
            # Hah!  We can automatically monitor it!
            return  (MonitoringRule.HIGHPRIOMATCH
                    ,    {   'monitorclass': 'ocf'
                            ,   'monitortype':  self.rsctype
                            ,   'provider':     self.provider
                            ,   'arglist':      arglist
                        }
                    )
        else:
            # We can monitor it with some more help from a human
            # Better incomplete than a sharp stick in the eye ;-)
            return (MonitoringRule.PARTMATCH
                    ,   {   'monitorclass': 'ocf'
                            ,   'monitortype':  self.rsctype
                            ,   'provider':     self.provider
                            ,   'arglist':      arglist
                        }
                    ,   missinglist
                    )

@MonitoringRule.RegisterFun
def argvalue(args, values, graphnodes):
    '''
    A function which searches a list for an argument of the form
    name=value.
    The name is given by the argument in args, and the list 'arglist'
    is assumed to be the list of arguments.

    If there are two arguments in args, then the first argument is the
    array value to search in for the name=value string instead of 'arglist'
    '''
    if len(args) > 2 or len(args) < 1:
        return None
    if len(args) == 2:
        argname = args[0]
        definename = args[1]
    else:
        argname = 'arglist'
        definename = args[0]
    if argname in values:
        listtosearch = values[argname]
    else:
        listtosearch = None
        for node in graphnodes:
            value = node.get(argname)
            if value is not None:
                listtosearch = value
                break
    if listtosearch is None:
        return None
    prefix = '%s=' % definename
    # W0702: No exception type specified for except statement
    # pylint: disable=W0702
    try:
        for elem in listtosearch:
            if elem.startswith(prefix):
                return elem[len(prefix):]
    except: # No matter the cause of failure, return None...
        pass
    return None

    

if __name__ == '__main__':
    from graphnodes import ProcessNode
    neoargs = (
                ('arglist[0]', r'.*/[^/]*java[^/]*$'),   # Might be overkill
                ('arglist[3]', r'-server$'),             # Probably overkill
                ('arglist[-1]', r'org\.neo4j\.server\.Bootstrapper$'),
        )
    neorule = LSBMonitoringRule('neo4j-service', neoargs)

    sshnode = ProcessNode('global', 'fred', '/usr/bin/sshd', ['/usr/bin/sshd', '-D' ]
    #ProcessNode:
    #   (domain, host, pathname, arglist, uid, gid, cwd, roles=None):
    ,   'root', 'root', '/', roles=(CMAconsts.ROLE_server,))

    sshargs = (
                # This means one of our nodes should have a value called
                # pathname, and it should end in '/sshd'
                ('pathname', '.*/sshd$'),
        )
    sshrule = LSBMonitoringRule('ssh', sshargs)

    udevnode = ProcessNode('global', 'fred', '/usr/bin/udevd', ['/usr/bin/udevd']
    ,   'root', 'root', '/', roles=(CMAconsts.ROLE_server,))


    neoprocargs = ("/usr/bin/java", "-cp"
    , "/var/lib/neo4j/lib/concurrentlinkedhashmap-lru-1.3.1.jar:"
    "/var/lib/neo4j/lib/geronimo-jta_1.1_spec-1.1.1.jar:/var/lib/neo4j/lib/lucene-core-3.6.2.jar"
    ":/var/lib/neo4j/lib/neo4j-cypher-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-graph-algo-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-graph-matching-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-jmx-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-kernel-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-lucene-index-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-shell-2.0.0-M04.jar"
    ":/var/lib/neo4j/lib/neo4j-udc-2.0.0-M04.jar"
    "/var/lib/neo4j/system/lib/neo4j-server-2.0.0-M04-static-web.jar:"
    "AND SO ON:"
    "/var/lib/neo4j/system/lib/slf4j-api-1.6.2.jar:"
    "/var/lib/neo4j/conf/", "-server", "-XX:"
    "+DisableExplicitGC"
    ,   "-Dorg.neo4j.server.properties=conf/neo4j-server.properties"
    ,   "-Djava.util.logging.config.file=conf/logging.properties"
    ,   "-Dlog4j.configuration=file:conf/log4j.properties"
    ,   "-XX:+UseConcMarkSweepGC"
    ,   "-XX:+CMSClassUnloadingEnabled"
    ,   "-Dneo4j.home=/var/lib/neo4j"
    ,   "-Dneo4j.instance=/var/lib/neo4j"
    ,   "-Dfile.encoding=UTF-8"
    ,   "org.neo4j.server.Bootstrapper")

    neonode = ProcessNode('global', 'fred', '/usr/bin/java', neoprocargs
    ,   'root', 'root', '/', roles=(CMAconsts.ROLE_server,))

    print 'Should be (2, {something}):	', sshrule.specmatch((sshnode,))
    print 'This should be (0, None):	', sshrule.specmatch((udevnode,))
    print 'This should be (0, None):	', sshrule.specmatch((neonode,))
    print 'This should be (0, None):	', neorule.specmatch((sshnode,))
    print 'Should be (2, {something}):	', neorule.specmatch((neonode,))