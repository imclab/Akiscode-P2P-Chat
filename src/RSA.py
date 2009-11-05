#-------------------------------------------------------------------------------------------------
# Name: Akiscode Chat
# Author: Stephen Akiki
# Website: http://akiscode.com
# Language: Python
# Usage: 
#	python akischat.py 
# Dependencies:
#	---
# Thanks to:
#	---
# Disclaimer:
#	By using this program you do so at your own risk. I assume no liability
#	for anything that happens to you because you used this program.
#	
#	Enjoy
#
# License - GNU GPL (See LICENSE.txt for full text):
#-------------------------------------------------------------------------------------------------
#    If you want to use this code (in compliance with the GPL) then you should
#    include this somewhere in your code comments header:
#
#    Thanks to Stephen Akiki (http://akiscode.com/code/chat) for peer-to-peer chat code
#-------------------------------------------------------------------------------------------------
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#-------------------------------------------------------------------------------------------------
# Copyright (C) 2009 Stephen Akiki. All rights reserved.
#-------------------------------------------------------------------------------------------------

import math
import random

def eeuclid(a, n, debug=False):
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


    return (p - 1) * (q - 1)

def coprime(t):
    nums = eratosthenes(t)
    return random.choice(nums)

def eratosthenes(n):
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
    n = p * q
    t = totient(p, q)
    if e is None:
        e = coprime(t)
    d = int(eeuclid(e, t)[0] % t) 
    return (n, e, d, str((n, e, d)))

def rsa(message, public, private, decrypt=False):
    if decrypt is False:
        return int(message**public[1] % public[0])
    else:
        return int(message**private[1] % private[0])

if __name__ == "__main__":
    import doctest
    doctest.testmod()

