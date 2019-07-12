Installing
==========

Installing kisee
----------------

First start by building a venv, let's say ``/tmp/kisee`` for the
example, but please find it a better place::

  python3 -m venv /tmp/kisee

and activate it::

  /tmp/kisee/bin/activate

To install ``kisee``, run::

  pip install kisee

Copy example settings::

  cp example-settings.toml settings.toml

Edit it, to at least generate a new private/public key pair)::

  editor settings.toml

Run it once manually to test it::

  kisee  # or python -m kisee

This will start a server on port 8140, you can kill it and now
configure systemd to start it.

In a file like ``/etc/systemd/system/kisee.service``, copy::

  [Unit]
  Description=Kisee
  After=network.target

  [Service]
  Type=simple
  ExecStart=/tmp/kisee/bin/python -m kisee
  WorkingDirectory=/home/kisee/kisee-19.07.0/

  Restart=on-abort
  User=kisee
  Group=kisee

  [Install]
  WantedBy=multi-user.target

Then reload systemd config, enable it and start it::

  systemctl daemon-reaload
  systemctl enable kisee
  systemctl start kisee


Configuring HTTPS using nginx with certbot
------------------------------------------

Using ``nginx`` as a front-end for ``kisee`` may be a good idea,
typically at least for HTTPS decapsulation.

First install nginx and certbot::

  apt install nginx certbot python3-certbot-nginx

First generate a nice dhparam if needed::

  [ -f /etc/ssl/certs/dhparam.pem ] || openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096

Make sure your domain resolves correcly to the machine, and generate
the certificate (replace EXAMPLE.COM in the command, if nginx is
running, replace --standalone with --nginx)::

  DOMAIN=EXAMPLE.COM; certbot certonly --cert-name $DOMAIN -n --agree-tos -d $DOMAIN \
    -m admin@$DOMAIN --standalone --rsa-key-size 4096

Create the nginx TLS snippet (replace ``EXAMPLE.COM``) in
``/etc/nginx/snippets/letsencrypt-EXAMPLE.COM.conf`` like this ::

    ssl_ciphers "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:AES256+EECDH:AES256+EDH";
    ssl_protocols TLSv1.1 TLSv1.2;

    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:ssl_session_cache:10m;
    ssl_certificate /etc/letsencrypt/live/EXAMPLE.COM/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/EXAMPLE.COM/privkey.pem;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

Make sure ``installer`` and ``authenticator`` are set to ``nginx`` in
``/etc/letsencrypt/renewal/EXAMPLE.COM.conf``, in the
``[renewalparams]`` section. ``installer`` may not exist, if so create
it near the ``authenticator`` one.

Finally configure nginx like this (again, replace EXAMPLE.COM)::

  server
  {
    listen 80;
    server_name EXAMPLE.COM;

    return 301 https://$server_name$request_uri;
  }

  server
  {
    listen 443 ssl;
    server_name EXAMPLE.COM;

    include snippets/letsencrypt-EXAMPLE.COM.conf;

    location /
    {
      proxy_pass http://127.0.0.1:8140;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header X-Forwarded-Protocol $scheme;
    }
  }


Testing your instance
---------------------

To check if your instance is running, just curl on it, over HTTPS from
the outside::

  curl https://kisee.example.com

this should give you the json-home of kisee, like this::

  {
      "api": {
      "title": "Identification Provider",
      "links": {
          "author": "mailto:julien@palard.fr",
          "describedBy": "https://kisee.readthedocs.io"
      }
  },
  [...]
