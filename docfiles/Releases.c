/**
@page ReleaseDescriptions Release Descriptions
@section Version_1_0 version 1.0 - the "Independence Day" release - 4 July 2015
This release provides a number of new features, and a number of bug fixes.
This release is eminently suitable for deployments in environments where the caveats are acceptable.
We have quite a few pre-built Ubuntu packages, and a few CentOS/RHEL packages for this version in the 1.0 subdirectory of 
http://bit.ly/assimreleases.
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v1.0.tar.gz
@subsection Features_1_0 New Features
- Support for <a href="https://trello.com/c/gBvVYLfFP">Nagios remote agent APIs</a> from Carrie Oswald <carrieao@comcast.net>.
  Not all Nagios agents are automatically configured, some are duplicates of generally superior OCF resource agents.
  You can easily add configuration for anything you want Nagios to monitor.
  This version includes automatic configuration of the following Nagios agents:
 - check_load (load average)
 - sensors (checking for temperatures, fan speeds, etc)
 - sshd (secure shell daemon/service)
- Added nagios to the set of discovery agents we discover using the monitoringagents discovery agent.
- Optimize initial nanoprobe setup time by <a href="https://trello.com/c/uIwMlDxQ">combining all the ARP and switch discovery requests into one packet</a>.
  In addition to being a significant optimization, it is also required for systems with large numbers of interfaces to avoid queue overflow.
- Provided some initial API documentation
- New discovery agents: PAM, /proc/partitions, mdadm, findmnt, nsswitch, commands, sshd configuration.
- Prototype (toy) code for evaluating best practices (security, network, etc.).
- <a href="https://trello.com/c/eq3Jn6Rf">added the location of where to report bugs to the web site</a>.
- Added a download link to the top right of every page. Thanks to Dimitri van Heesch for teaching us how to do that.
-  <a href="https://trello.com/c/0pcKwdLK"> Eliminated a number of redundant startup messages.</a>
- Minor change to allow us to build under docker for precise, trusty, utopic, and vivid
- Added a number of new unit test cases - particularly for discovery agents.

@subsection BugFixes_1_0 Bug Fixes
- <a href="https://trello.com/c/nmbxX6kY">Flask queries with parameters don't work</a> - also added code to limit the max size of JSON_ node attributes in query results.
- <a href="https://trello.com/c/3tIhv3Jp">pcap_lookupnet() failure should not be fatal</a>
- <a href="https://trello.com/c/Htc1T9H9">Timestamps in discovery results were never set</a>.
- <a href="https://trello.com/c/upkwQiZA">Code was not listening to ARP or LLDP/CDP packets</a>.
  This probably wasn't an issue in the last release, but got introduced between releases.
- <a href="https://trello.com/c/AxcvC9zW">resources monitored by invalid monitoring requests aren't marked as down</a>.
  This only can occur when the CMA and nanoprobe versions are out of sync with each other - like in the middle of adding nagios support for example ;-).
- Fixed a number of bugs associated with testing (not real code bugs).
- Corrected a number of dependencies for building and final packages.

@subsection Caveats_1_0 Caveats
- No alerting, or interface to existing alerting (hooks to build your own interface are included)
- high availability option for the CMA is roll-your-own using Pacemaker or similar
- queries could benefit from more indexes for larger installations.
- The CMA may suffer performance problems when discovering IP addresses when large numbers of nanoprobes are on a subnet.
- no GUI
- use with recent versions of Neo4j requires disabling authentication on Neo4j

@section Version_0_5 version 0.5 - the "Valentine's day" release - 14 February 2015
This is release is sixth in a series of releases intended to culminate in an awesomely useful release.
It is primarily a bug fix release.
This release is eminently suitable for deployments in environments where the caveats are acceptable.
We have quite a few pre-built Ubuntu packages, and a few CentOS/RHEL packages for this version in the 0.5 subdirectory of 
http://bit.ly/assimreleases.
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v0.5.tar.gz
@subsection Features_0_5 New Features
- We now produce Docker images for several versions of Linux, suitable for doing demos, testing, and learning about the software.
@subsection BugFixes_0_5 Bug Fixes
- Fixed a bug where command line (assimcli) queries sometimes failed due to interactions with Linux security modules
- Fixed a longstanding-but-previously-unknown bugs where it didn't like floating point numbers or negative integers in JSON
@subsection Caveats_0_5 Caveats
- No alerting, or interface to existing alerting (hooks to build your own interface are included)
- high availability option for the CMA is roll-your-own using Pacemaker or similar
- the queries need to have more indexes for larger installations.
- The CMA may suffer performance problems when discovering IP addresses when large numbers of nanoprobes are on a subnet.
- no GUI
@section Version_0_1_5- version 0.1.5 - the 'secure communications' release - 29 January 2015
This is the fifth in a series of releases intended to culminate in an awesomely useful release.
This release is eminently suitable for actual deployments in an environment where the caveats are acceptable.
We have quite a few pre-built Ubuntu packages, and a few CentOS/RHEL packages for this version in the 0.1.5 subdirectory of 
http://bit.ly/assimreleases .
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v0.1.5.tar.gz
@subsection Features_0_1_5 New Features
- Encrypted Communication.  Communication between the CMA and nanoprobes are now strongly encrypted using curve25519.
- Added <tt>genkeys</tt> option to <tt>assimcli</tt>
- Added new queries to <tt>assimcli</tt>
- Added discovery of /proc/sys data
- Added feature for debugging in the field (circular FSA buffer)
- Increased kernel buffering for the CMA
- Improved system testing code
- Improved scrubbing of network packets
- Improved diagnostics on startup failures
- Added the ability to take core dumps to the CMA and nanoprobe init scripts
@subsection BugFixes_0_1_5 Bug Fixes
- Several protocol holes were plugged.
- Fixed coverity-flagged issues: 1262409, 1262410, 1262411, 1262412, 1262413
- Fixed a few queries in <tt>assimcli</tt>
@subsection Caveats_0_1_5 Caveats
- No alerting, or interface to existing alerting (hooks to build your own interface are included)
- high availability option for the CMA is roll-your-own using Pacemaker or similar
- the queries need to have more indexes for larger installations.
- The CMA may suffer performance problems when discovering IP addresses when large numbers of nanoprobes are on a subnet.
- no GUI

@section Version_0_1_4- version 0.1.4 - the 'much better tested' release - 20 October 2014
This is the fourth in a series of releases intended to culminate in a truly useful release.
This release is eminently suitable for trials in an environment where the caveats are acceptable.
We have quite a few pre-built Ubuntu packages, and a few CentOS/RHEL packages for this version in the 0.1.4 subdirectory of 
http://bit.ly/assimreleases .
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v0.1.4.tar.gz

A complete and detailed view of the features, bugs, caveats and so on for the Assimilation
Project is currently held on on <a href="https://trello.com/b/98QrdEK1/issues-bugs">Trello</a>.
The lists of special interest are the <b>In release 0.4</b> list and the various other bug and caveat lists in
<a href="https://trello.com/b/98QrdEK1/issues-bugs">this board</a>.

@subsection Features_0_1_4 Features
- 100+ system System-level testing environment now part of development process
- We now create several CentOS packages in our official build environment
- Added support for Cisco's CDP (Cisco Discovery Protocol) for discovering switch connections in Cisco environments
- Builds now support RHEL6/7 environments
- Detailed documentation on building and installing for RHEL6.
- ARP IP/MAC discovery on multiple interfaces (previously hard-wired to eth0)
- LLDP/CDP discovery on multiple interfaces (previously hard-wired to eth0)
- Added timeouts to discovery processes
- Canned queries can now return simple (non-node) values.
- Bugs and features in this release now logged in <a href="https://trello.com/b/98QrdEK1/issues-bugs">Trello</a>.
- Documentation updates.

@subsection BugFixes_0_1_4 Bug Fixes
- Several canned queries now fixed
- Removed duplicate ipport entries in database
- Nanoprobes now stop reliably
- ARP discovery flooding now mitigated
- Numerous fixes related to the reliable communications protocol
- Numerous other small fixes.

@subsection Caveats_0_1_4 Caveats
- communication is neither authenticated nor confidential
- No alerting, or interface to alerting (hooks to build your own interface are included)
- high availability option for the CMA
- the queries need to have more indexes for larger installations.
- statistical data collection
- The CMA may suffer performance problems when discovering IP addresses when large numbers of nanoprobes are on a subnet.
- Object deletion not yet reliable or complete

Features that are expected for a monitoring solution but are <b>not</b> included include these:
- useful alerting (but you can probably integrate your own)
- Alerting history.
- non-Linux system support (POSIX and Windows - but now someone is working on Windows!)
- statistical data collection
Note that these features are understood to be important and are planned - but this release
does not include them.

@section Version_0_1_3- version 0.1.3 - the 'even more interesting' release - 02 May 2014 [32 April 2014;-)]
This is the third in a series of releases intended to culminate in a truly useful release.
This release is suitable for trials in an environment where the caveats are acceptable.
We have quite a few pre-built Ubuntu packages for this version here:
https://www.dropbox.com/sh/4olv5bw1cx8bduq/AADYcxtYYwlFZxV-P0LpRA4ra/builds/Releases/0.1.3
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v0.1.3.tar.gz
@subsection Features_0_1_3 Features
These features are new with release 0.1.3.
- ARP discovery - we listen to ARP packets (including broadcasts) and add the IP addresses we find to the CMDB
- Package discovery - we discover what packages you have installed and add the results to the database
- Packet compression - we now allow discovery packets of JSON up to about 300K through compression.
- Works on CentOS 6.5 and related RedHat-derived systems
- Works on Fedora 20 (and probably other Fedora releases as well)
- Updated documentation - GettingStarted (thanks Ken Schumacher) and other places
- Dockerfiles for Fedora and CentOS
@subsection BugFixes_0_1_3 Bug Fixes
- Fixed problems which kept strict compilation flags from being used
@subsection Caveats_0_1_3 Caveats
- Object deletion not yet reliable or complete
- No alerting, or interface to alerting (hooks to build your own interface are included)
- communication is neither authenticated nor confidential
- heterogeneous system support (POSIX and Windows - but now someone is working on Windows!)
- statistical data collection
- CDP support for Cisco switch discovery
- high availability option for the CMA
- the queries need to have more indexes for larger installations.

Features that are expected for a monitoring solution but are <b>not</b> included include these:
- useful alerting (but you can probably integrate your own)
- heterogeneous system support (POSIX and Windows - but someone is now looking at Windows - yay!)
- statistical data collection
Note that these features are understood to be important and are planned - but this first release
does not include them.

@section Version_0_1_2- version 0.1.2 - the 'very interesting' release - 20 March 2014
These features are new with release 0.1.3.
This is the second in a series of releases intended to culminate in a truly useful release.
This release is suitable for limited trials in an environment where the caveats are acceptable.
you can find quite a few pre-built Ubuntu packages for this version here: https://www.dropbox.com/sh/h32lz3mtb8wwgmp/26AyspFaxL/Releases/0.1.2
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v0.1.2.tar.gz
@subsection Features_0_1_2 Features
These features are new with release 0.1.2.
- added <i>assimcli</i> - a command line query tool with more than 15 cool canned queries.  These queries are also available through the REST interface.
 - allipports:     get all port/ip/service/hosts
 - allips: get all known IP addresses
 - allservers:     get known servers
 - allservicestatus:       status of all monitored services
 - allswitchports: get all switch port connections
 - crashed:        get 'crashed' servers
 - down:   get 'down' servers
 - downservices:   get 'down' services
 - findip: get system owning IP
 - findmac:        get system owning MAC addr
 - hostdependencies:       host's service dependencies
 - hostipports:    get all port/ip/service/hosts
 - hostservicestatus:      monitored service status on host
 - hostswitchports:        get switch port connections
 - list:   list all queries
 - shutdown:       get gracefully shutdown servers
 - unknownips:     find unknown IPs
 - unmonitored:    find unmonitored services
- added a checksum monitoring capability - for network-facing binaries, libraries and JARs.
- updated to a newer and faster version of the py2neo library
- updated the CMA to use the Glib mainloop event scheduler
- added a certain amount of Docker compatibility.  Assimilation now builds and installs correctly for CentOS 6 (but some tests seem to fail).

@subsection BugFixes_0_1_2 Bug Fixes
- Fixed the memory leak from 0.1.1 - which turned out to be minor.
- Fixed a subtle bug in the Store class where it would appear to lose values put into node attributes
- Fixed lots of bugs in the REST queries - and renamed them to be more command line friendly
@subsection Caveats_0_1_2 Caveats
- Object deletion not yet reliable or complete
- No alerting, or interface to alerting (hooks to build your own interface are included)
- communication is neither authenticated nor confidential
- heterogeneous system support (POSIX and Windows - but now someone is working on Windows!)
- statistical data collection
- CDP support for Cisco switch discovery
- high availability option for the CMA
- the queries need to have more indexes for larger installations.

Features that are expected for a monitoring solution but are <b>not</b> included include these:
- useful alerting (but you can probably integrate your own)
- heterogeneous system support (POSIX and Windows - but someone is now looking at Windows - yay!)
- statistical data collection
Note that these features are understood to be important and are planned - but this first release
does not include them.

@section Version0_1_1- version 0.1.1 - the 'possibly trial-worthy' release - 11 Feb 2013
This is the first in a series of releases intended to culminate in a truly useful release.
This release is suitable for limited trials in an environment where the caveats are acceptable.
You can find a few pre-built Ubuntu packages for this version here: https://www.dropbox.com/sh/h32lz3mtb8wwgmp/WZKH4OWw1h/Releases/0.1.1
A tar ball for this version can be found here: http://hg.linux-ha.org/assimilation/archive/v0.1.1.tar.gz

@subsection Features_0_1_1 Features
These features are new with release 0.1.1.
- new Neo4j schema
- service monitoring
- automatic (zero-config) service monitoring through templates
- basic fork/exec event notification feature - /usr/share/assimilation/notification.d
- hooks for more sophisticated event notification
- added Pylint analysis and verification
- added Coverity static analysis
- added root ulimit discovery
- added discovery of locally installed monitoring agents
- integration of all tests under testify
- added a Neo4j OCF resource agent
- added Flask code to support the creation of a JavaScript User Interface
- Added Query objects in support of the Flask code.
- Added the ability for for the Flask code to invoke Query objects and get results
- significant internal improvements in Neo4j access
- allow parsing of MAC addresses - they're now all in XX-YY-ZZ (etc) format.
- Added transactions for the database and the network
- removed "Monitoring" from the project name (but not from its capabilities)

@subsection BugFixes_0_1_1 Bug Fixes
- check to make sure requested discovery scripts are present before executing them
- much improved tcp service discovery
- fixed a number of 64-bit-only assumptions in the code and tests
- improved compatibility with old versions of Ubuntu
- All graph node creation now checks to see if it already exists - avoiding accumulating superfluous objects
- lots of other bugs associated with new features ;-)

@subsection Caveats_0_1_1 Caveats
- The CMA has a known slowish memory leak.  It'll still take it a long time to grow larger than a small Java program ;-)
  More importantly, it is very unlikely to happen <i>at all</i> in a production system.
- You will have to recreate your Neo4j database from scratch to convert to this release.
- Object deletion not yet reliable or complete
- No alerting, or interface to alerting (hooks to build your own interface are included)
- communication is neither authenticated nor private
- heterogeneous system support (POSIX and Windows)
- statistical data collection
- CDP support for Cisco switch discovery
- high availability option for the CMA

Features that are expected for a monitoring solution but are <b>not</b> included include these:
- useful alerting (but you can probably integrate your own)
- heterogeneous system support (POSIX and Windows)
- statistical data collection
Note that these features are understood to be important and are planned - but this first release
does not include them.

@section Version0_1_0- version 0.1.0 - the 'toy' release - 19 March 2013
The very first release of the <i>Assimilation Monitoring Project</i> - here at last!
The purpose of this Linux-only release is to get the code from this
revolutionary new architecture out there and get it in people's hands so
that they can evaluate the concepts, provide feedback, and find bugs.
It is highly recommended that you read the @ref GettingStarted documentation.
@subsection Features_0_1_0 Features
- easily extensible discovery mechanism
- Neo4J graph database documenting the data center configuration
- fully distributed, extremely lightweight, reliable monitoring
- <b>no</b> configuration needed for most environments - very simple configuration for all environments.
- basic <i>host</i> monitoring
- continuous, integrated stealth discovery of these kinds of information:
 - host network configuration - NICs, IP addresses, MAC addresses
 - host OS version information
 - basic hardware
 - ARP cache information
 - detailed information about TCP services offered (server role)
 - detailed information about TCP services consumed (client role)
 - LLDP-based server/switch topology discovery - which host NICs are connected to which switch ports
 - Tested extensively on Linux systems.
 - Source code known to compile on Windows systems (will eventually run there too).

Features that are expected for a monitoring solution but are <b>not</b> included include these:
- meaningful alerting
- service monitoring
- heterogeneous system support (POSIX and Windows)
- statistical data collection
- CDP support for switch discovery
- high availability option for the CMA

Note that these features are understood to be important and are planned - but this first release
does not include them.

@subsection BugFixes_0_1 Bug Fixes
Since this is the first release, you could consider everything a bug fix - or nothing -- take your pick.
@subsection Caveats_0_1 Caveats
This is the very first baby release of the project - nicknamed the <i>toy</i> release for a reason.
Although the code looks very stable for a release of this nature, and is unlikely to consume
vast quantities of resources or crash your machines - it has never seen real field action before -
and such results are not out of the realm of possibility for any software - much less
for software so new as this release.

It is recommended that you deploy this release on test machines until sufficient feedback has been
received to determine how it plays out in the field.

Other more mundane caveats:
- efficiency - the code is currently wildly inefficient compared to what it should be to achieve its scalability goals
  There are many known issues in this area.
- service discovery duplication
- no doubt many others which are not known, or have been forgotten about
- CMA restart might lose data from nanoprobes for discovery or system outages

*/
