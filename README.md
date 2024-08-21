# GBN ARQ Protocol 

### From [Wikipedia](https://en.wikipedia.org/wiki/Go-Back-N_ARQ#:~:text=Go%2DBack%2DN%20ARQ%20is,the%20peer%20before%20requiring%20an%20ACK.)

>"_Go-Back-N ARQ is a specific instance of the automatic repeat request (ARQ) protocol, in which the sending process continues to send a number of frames specified by a window size even without receiving an acknowledgement (ACK) packet from the receiver. It is a special case of the general sliding window protocol with the transmit window size of N and receive window size of 1. It can transmit N frames to the peer before requiring an ACK._"

This project is my attempt to implement the Go Back-N ARQ Protocol that works around with data sent from the Application-Layer at the source to the Application-Layer at the destination address.

While I was working on this project, I gathered some helpful resources and put them on [this google doc page](https://docs.google.com/document/d/1AHe0np6HijeZhNoe1dcFBgBWi6Vx1aejOqx8oMyDEVs/edit?usp=sharing). Appreciate these works because they really helped me understand concepts such as Sequence Numbers and Acknowledgement Numbers, Sliding Windows, and more. Copyrights go to their respective original authors.
