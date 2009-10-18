"""
RSA public key cipher

>>> k = keygen(61, 53)
>>> public = (k[0], k[1])
>>> private = (k[0], k[2])
>>> ciphertext = rsa(123, public, None)
>>> rsa(ciphertext, None, private, decrypt=True)
123
"""

import math
import random

def eeuclid(a, n, debug=False):
    """Finds the GCD or multiplicative inverse of a number mod n
    
    Returns a two-element sequence in the format 
        (r, i)
    where r either the gcd or inverse, and i is True if result is
    inverse, False if result is gcd.

    >>> eeuclid(24141, 40902)
    (3.0, False)
    >>> eeuclid(7, 2311)
    (-330.0, True)
    """
    a1, a2, a3 = 1, 0, n
    b1, b2, b3 = 0, 1, a
    while b3 > 1:
        q = math.floor(a3/b3)
        t1, t2, t3 = (a1 - (q * b1), a2 - (q * b2), a3 - (q * b3))
        a1, a2, a3 = b1, b2, b3
        b1, b2, b3 = t1, t2, t3
    if b3 == 1:
        if debug:
            print 'return inverse'
        return (b2, True)
    if b3 == 0:
        if debug:
            print 'return gcd'
        return (a3, False)

def totient(p, q):
    """Returns the Euler totient of two numbers

    >>> p = 7
    >>> q = 5
    >>> totient(p, q)
    24
    """
    return (p - 1) * (q - 1)

def coprime(t):
    """Finds a possible coprime of a number

    >>> p = coprime(23)
    >>> eeuclid(p, 23)[1]
    True
    """
    nums = eratosthenes(t)
    return random.choice(nums)

def eratosthenes(n):
    """Generates a list of primes less than or equal to n

    Uses the Sieve of Eratosthenes.

    >>> eratosthenes(30)
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    """
    nums = range(2, n)
    p = t = 2
    while p**2 <= n:
        while t <= n:
            s = t * p
            if s in nums:
                del nums[nums.index(s)]
            t += 1
        p = t = nums[nums.index(p) + 1]
    return nums

def keygen(p, q, e=None):
    """Generate a key pair from two distinct prime numbers

    Returns a 4-element sequence in the following format:
        (n, e, d, str)
    where n is the modulo for the finite field, e is the
    public key exponent and d is the multiplicative inverse.
	str is a string consisting of (n,e,d).

    e may be also provided as an optional parameter.

    >>> keygen(61, 53, e=17)
    (3233, 17, 2753)
    """
    n = p * q
    t = totient(p, q)
    if e is None:
        e = coprime(t)
    d = int(eeuclid(e, t)[0] % t) 
    return (n, e, d, str((n, e, d)))

def rsa(message, public, private, decrypt=False):
    """Encrypts or decrypts a message with RSA

    The public and private key format is in
        (n, k)
    where n is the product of two primes and k is either the
    public key exponent (for encryption) or it's multiplicative
    inverse (for decryption)

    Private key can be None for encryption since it is not used.
    Likewise, public key can be None for decryption
    
    >>> public = (3233, 17)
    >>> private = (3233, 2753)
    >>> rsa(123, public, private)
    855
    >>> rsa(855, public, private, decrypt=True)
    123
    """
    if decrypt is False:
        return int(message**public[1] % public[0])
    else:
        return int(message**private[1] % private[0])

if __name__ == "__main__":
    import doctest
    doctest.testmod()

