# Networking Interview Questions

## What happens when you type a URL in your browser and press Enter?

### Assumptions
Network status:
- Our computer is connected to the network via Ethernet.
- Our computer already has an IP address.
- Our computer sits behind a NAT (this is the case in many home networks).
- Our ARP cache is clear.
- Our DNS cache is clear.
- Our router’s ARP cache contains an entry for its default gateway.
- Our network is `192.168.0.0/24`.
- The URL we’re going to use is `http://www.example.com`.
- The DNS server’s cache has an entry for `www.example.com`.
- We’re going to ignore TCP sequence numbers.

Configuration for our computer making the HTTP request:
- IP Address: `192.168.0.10`.
- Default gateway: `192.168.0.1`.
- DNS Server: `8.8.8.8`.
- MAC Address: `AA:AA:AA:AA:AA:AA`.
- TCP source port: `9999`.
- DNS source port: `3333`.

Configuration for our router / NAT:
- Internal IP Address: `192.168.0.1`.
- External IP address: `51.0.0.20`.
- External TCP source port: `15000`.
- External DNS source port: `10000`.
- External net mask: `255.255.255.0` (or `/24`).
- Internal MAC address: `BB:BB:BB:BB:BB:BB`.
- External MAC address: `CC:CC:CC:CC:CC:CC`.
- Default gateway: `51.0.0.1`.
- Default gateway’s MAC address: `DD:DD:DD:DD:DD:DD`.

The IP address of www.example.com is `93.184.216.34`.

Upon receiving the URL, the browser creates a HTTP request.
Our computer will then try to connect to www.example.com in TCP port 80. To initiate a TCP connection, we need to do a three-way handshake. The first step of the handshake is to send a SYN segment (SYN bit set to 1). Our TCP segment will have 9999 as the source port and 80 as the destination port.
This TCP segment will then be encapsulated in an IP datagram (source IP address: 192.168.0.10). As we do not yet know what the destination IP address is, our computer goes to its DNS cache to look for the IP address for example.com. Since the DNS cache is clear, for now our IP datagram is incomplete.
To get an IP address for example.com, we use a service called DNS. Our computer creates a DNS query message, putting the name to be resolved (www.example.com) in the question section of the DNS message. This DNS message is then placed within a UDP segment (source port: 3333, destination port: 53). This segment is encapsulated in a IP datagram (source IP address: 192.168.0.10, destination IP address: 8.8.8.8).
Now our computer wants to send this IP datagram, but it does not know where to send it to. The computer looks at its routing table, to see which route matches the 8.8.8.8 IP address. Our computer uses the longest prefix match (wiki) to do so, and it decides to send the datagram to the default gateway (192.168.0.1). From there, the router will take care of forwarding it the next hop.

| Destination | Netmask | Gateway | Interface |
| --- | --- | --- | --- |
| 0.0.0.0 | 0.0.0.0 | 192.168.0.1 | eth0 |
| 192.168.0.0 | 255.255.255.0 | 0.0.0.0 | eth0 |

Now that our IP datagram is ready, it’s wrapped in an Ethernet frame (source MAC address: AA:AA:AA:AA:AA:AA). To figure out the destination MAC address (router MAC address), our computer looks at its ARP table to see whether it has an entry to convert the gateway router’s IP address (192.168.0.1) to a MAC address. Since the ARP cache is empty, for now our Ethernet frame is incomplete.
Our computer creates an ARP query message with a destination IP address of 192.168.0.1 (the default gateway).
The ARP message is placed within an Ethernet frame with a broadcast destination address (FF:FF:FF:FF:FF:FF) and sends the Ethernet frame to the switch, which delivers the frame to all connected devices, including the gateway router.
When the gateway router receives the frame containing the ARP query message, it prepares an ARP reply, indicating that its MAC address of BB:BB:BB:BB:BB:BB corresponds to IP address 192.168.0.1.
The gateway router places the ARP reply message in an Ethernet frame, with a destination address of AA:AA:AA:AA:AA:AA (our computer) and sends the frame to the switch, which delivers the frame to our computer.
Upon receiving the frame, our computer saves the MAC address of the gateway router in its ARP cache. Our computer also completes the Ethernet frame containing the DNS message, with the destination MAC address set to BB:BB:BB:BB:BB:BB (the gateway router). Note that the destination IP address for the IP datagram encapsulated within this frame is 8.8.8.8 (the DNS server).
The gateway router receives the frame and extracts the IP datagram containing the DNS query. From the destination IP address on the datagram, the router determines using the longest prefix match that the frame should be forwarded to its default gateway (51.0.0.1).
Since we assume that our router is also a NAT, the IP address needs to be translated before sending to the public Internet. NAT translates private addresses to public addresses. Using the NAT translation table, our router replaces the source IP address of the datagram (192.168.0.10) with the public IP address (51.0.0.20), and the internal source port (3333) with the external source port (10000). The external source port is chosen randomly to make sure the connection identifier is unique.
Our router wraps the datagram in a new Ethernet frame (source MAC address: CC:CC:CC:CC:CC:CC, destination MAC address: DD:DD:DD:DD:DD:DD). We assumed this value was already cached so there’s no need for ARP.
The Ethernet frame is sent to the default gateway which is most likely a router owned by our ISP and it is up to the ISP to get our packet to 8.8.8.8.
Once our packet reaches the DNS server (8.8.8.8), the server extracts the DNS query, looks up the name www.example.com in its DNS database, and finds the DNS resource record that contains the IP address (93.184.216.34) for www.example.com (we assume that it is currently cached in the DNS server).
The DNS server forms a DNS reply message containing this hostname-to-IP-address mapping, and places the message in a UDP segment (source port: 53, destination port: 10000), and the segment within an IP datagram (source IP address: 8.8.8.8, destination IP address: 51.0.0.20). The datagram is finally wrapped in an Ethernet frame and sent through the network.
The frame reaches our router. Our router needs to translate this frame. Using the NAT translation table, the router translates the destination IP to be our computer’s IP (192.168.0.10) and the destination port to be our computer’s source port (3333). After this, the router wraps the datagram in an Ethernet frame (source MAC: BB:BB:BB:BB:BB:BB, destination MAC: AA:AA:AA:AA:AA:AA) and sends it to our computer.
With the IP address of www.example.com, our computer stores it on its DNS cache. Our computer also fills in the incomplete SYN segment. The IP datagram is wrapped in an Ethernet frame and sent through the private network.
Our router receives the packet and extracts the IP datagram. Using NAT translation table, our router replaces the source IP of the datagram from 192.168.0.10 to 51.0.0.20, and the source port from 9999 to 15000. The modified datagram is wrapped in an Ethernet frame (source MAC address: CC:CC:CC:CC:CC:CC, destination MAC address: DD:DD:DD:DD:DD:DD).
When the packet reaches 93.184.216.34 (the IP address of www.example.com), the server looks at the destination port of the TCP segment (80) and checks if an application is listening on that port. Since there is an HTTP server running on that port, the server needs to reply with a SYN/ACK segment. The server creates a TCP segment (source port: 80, destination port: 15000), and the SYN and ACK bit set to 1. It then wraps the segment in an IP datagram (source IP: 93.184.216.34, destination IP: 51.0.0.20). Finally, it wraps the datagram in an Ethernet frame. The packet is then sent out to the network.
When the packet reaches our router, it performs a translation using the NAT translation table. The destination port and IP address is changed (15000 -> 9999, 51.0.0.20 -> 192.168.0.10).
Upon receiving the packet, our computer looks at the destination port (9999) and the TCP flags (SYN/ACK) and checks the state of this connection. The only thing missing to establish this connection is to send an ACK back to the server (93.184.216.34). Our computer creates a new TCP segment. The segment is wrapped in an IP datagram. The datagram is wrapped in an Ethernet frame and sent over the private network. Our computer then marks the connection as ESTABLISHED.
Our router performs NAT translation and replaces the source port and source IP address.
The frame traverses the Internet until it gets to 93.184.216.34. Note that the server doesn’t return an ACK for the ACK it just received.

Our computer is now ready to send the actual HTTP request.
It wraps the HTTP request in a TCP segment (destination port: 80, ACK=1). The PSH bit is set to 1, as the receiver of this segment should pass the data to the upper layer immediately. The segment is then wrapped in an IP datagram (destination IP address: 93.184.216.3), which is then wrapped in an Ethernet frame.
Upon arriving on the router, it performs NAT translation.
The packet reaches 93.184.216.3.

The HTTP server processes the HTTP request and generates an HTTP response.
This HTTP response is wrapped in a TCP segment (PSH=1, ACK=1), which in turn is wrapped in an IP datagram, which in turn is wrapped in an Ethernet frame.
Upon arriving on the router, the frame undergoes NAT translation.
Our computer receives the packet and looks up the connection information. The PSH flag instructs our computer to send the TCP body (the HTTP response) to the application that opened the connection (our web browser).

Our web browser now has the HTTP response and can use it to render the web page. (From the networking side, however, we’re not done. The server doesn’t know that we received the TCP segment since we haven’t acknowledged it, i.e. sent an ACK back. And since the browser is not going to send more requests to www.example.com, it will also close the connection.)

There is some overhead while establishing the TCP connection. HTTP clients try to keep the connection alive (with the Connection: Keep-Alive HTTP header) to avoid this overhead and reuse the same connection. A problem with this header is that HTTP clients can only make one request a time (per TCP connection). HTTP/2 solves this problem by multiplexing the connection.

## What do you understand by `ping` command?

The ping command instructs OS to generate an ICMP packet type 8 code 0. ICMP is architecturally above IP. ICMP is usually used for error reporting. For example, when an IP router is unable to find a path to the host specified in the HTTP request.

## What is a firewall?

## What is UDP? What are the advantages and disadvantages of UDP?
UDP is a no-frills, lightweight transport protocol, providing minimal services. Why would a developer ever choose to build an application over UDP rather than over TCP?
Finer application-level control over what data is sent, and when. UDP packages data inside a UDP segment and immediately passes the segment to the network layer. TCP, on the other hand, has a congestion-control mechanism that throttles the transport-layer TCP sender.
No connection establishment. Unlike TCP, UDP does not introduce any delay to establish a connection, hence it’s faster.
No connection state. Hence UDP does not track any parameters. For this reason, a server devoted to a particular application can typically support many more active clients when the application runs over UDP rather than TCP.
Small packet header overhead. UDP has only 8 bytes of header overhead in every segment, whereas TCP has 20 bytes of overhead.

## What’s the difference between TCP and UDP?
- Connection-oriented (handshaking before application-level messages begin to flow) vs connectionless
- Reliable (guarantees arrival, without error, in proper order) vs unreliable
- Congestion-control (control rate of output) vs no congestion-control
- Heavyweight vs lightweight
- HTTP vs DNS

## Why do we need 3 steps in a three-way handshake, why not 2?
A two-way handshake would only allow one party to establish an ISN, and the other party to acknowledge it; which means only one party can send data. However, TCP is a full-duplex communication protocol, which means both ends ought to be able to send data reliably. Both parties need to establish an ISN, and both parties need to acknowledge the other's ISN.

## Why do we need 4 steps to close a TCP connection, why not 3?
Both parties need to deallocate resources such as buffers and variables. When one party wants to close the connection, it sends a FIN segment and expects an ACK. Likewise for the other party. It can’t be three steps because although the client wants to terminate the connection, the server’s receiving buffer is not fully handled yet and the server is uncertain on the time it will take to end the connection from its side.

## Why do you need sequence numbers in TCP? Why not just start at 0?
Sequence numbers provide 2 features: (1) detecting when a message was lost, e.g., I got messages 1, 2 & 4, but not 3; (2) detecting when messages are duplicated, e.g., I got 3 copies of message 1, I can toss the extras. The receiver can tell the sender when it is missing a message and ask for it to be sent again. Detecting and discarding duplicates means the sender can retransmit without fear of messing up the receiver.

Guessing a sequence number makes it easy to spoof traffic (link).

## What is an API? Why do we need API?
Flight deal sites process your travel info and returns list of available flights sorted by price, airline, or layovers. This is possible because of APIs. API is a software intermediary that allows two applications to talk to each other. In this case, flight deal sites communicate with each airline’s website.

## Reasons we need APIs:
- APIs take advantage of a platform’s implementation to do the nitty-gritty work. Hence, they allow developers to save time.
- This helps reduce the amount of code developers need to create.
- This helps create more consistency across apps for the same platform.

## What is REST?
A REST API is a web service that uses the REST (Representational State Transfer) architecture to handle a request on a web service. It’s a set of recommendations and constraints for RESTful web services. These include:
Client-server architecture. System A makes an HTTP request to a URL hosted by System B, which returns a response.
Statelessness. Each request from any client contains all the information necessary to service the request.
Cacheable. Responses must define themselves as either cacheable or non-cacheable to prevent clients from providing stale or inappropriate data in response to further requests.
Layered system. A client cannot tell whether it is connected directly to the end server, or to an intermediary along the way. If a proxy or load balancer is placed between the client and server, it won't affect their communications and there won't be a need to update the client or server code.

HTTP-based RESTful APIs are defined with the following aspects:
- a base URI, such as http://api.example.com/collection/;
- standard HTTP methods (e.g., GET, POST, PUT, PATCH and DELETE).

## What are the HTTP methods? What is the difference between PUT, POST, and PATCH?
- The GET method requests a representation of the specified resource. Requests using GET should only retrieve data.
- The POST method is used to submit an entity to the specified resource, often causing a change in state or side effects on the server. Often used to create a resource.
- The PUT method replaces all current representations of the target resource with the request payload.
- The PATCH method is used to apply partial modifications to a resource.
- The DELETE method deletes the specified resource.

## What are the seven layers of OSI?
Application, Presentation, Session, Transport, Network, Data Link, Physical.
