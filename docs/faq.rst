FAQ
===

Can I use Kisee to query an OAuth2 service?
-------------------------------------------

Kisee is an identity provider, like twitter or github, so they're side
by side, not one on top of the other, they play the same role. You can
however use `Pasee <https://github.com/meltygroup/pasee>`_ on top of
Kisee and Twitter for example.


Does Kisee implement groups?
----------------------------

No, Kisee doesn't care about your groups like Github don't care about
your groups, they're both just here to say "yes, it's this user" or
"no, it is not".

From the `Pasee`_ point of view you'll be able to tell:

- User foo from Kisee is in group staff
- User bar from Github is in group staff too


Does Kisee implement impersonation?
-----------------------------------

No, if we do implement this we'll probably do in `Pasee`_ to rely on
`Pasee`_ groups to tell who can impersonate.


Does Kisee expose self-service registration?
--------------------------------------------

Optionally, only if you implement it or use a backend class
implementing it.


Does Kisee expose a password reset feature?
-------------------------------------------

Yes, by sending an email that you can template in the settings.
