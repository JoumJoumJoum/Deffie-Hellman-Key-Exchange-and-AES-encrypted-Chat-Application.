# Deffie Hellman Key-Exchange and AES encrypted Chat Application.

Built this Project as a way to familiarize myself with encryption methods. It's more focused on the on the Key Exchange and AES encryption part.

---

The Diffie Hellman Algorithm is a method used to ensure simple yet crucial connection by providing both endpoints with a shared key. One of the strengths of Diffie-Hellman is that even if an attacker intercepts the exchanged values, they would still be unable to deduce the final shared key without knowing each party’s private number, protecting against Man-in-the-Middle (MITM) attacks.

The algorithm begins with 2 users exchanging a shared prime (`m`) number and a shared base (`b`). The Server.py file generates these numbers and sends it to the client over a public network. It’s important to note that these values can be safely transmitted openly because they don’t reveal any sensitive information on their own and do not compromise the security of the final key.

Next, both the server and the client independently select a private secret value c for themselves. This number is never shared or transmitted across the network. Using this private value, each participant computes a public value using the formula:

``` public_value = pow(b,c,m) ```

For example:
Let’s assume both parties agree on a prime number ```m = 23``` and a base number ```b = 5```.
Now, the server picks a private value ```c = 6```, while the client picks ```c = 15```.

Server:                    

```pow(5, 6, 23) = 8```           

Client:

```pow(5, 15, 23) = 2```


These values are again exchanged between both the servers to compute the final shared key using the formula:

```pow(new,c,m)```

in our example: 

pow(2, 6, 23) = 13

pow(8, 15, 23) = 13


At this moment both the servers now share the same key.

---
