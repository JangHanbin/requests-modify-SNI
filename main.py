
import http.client

import requests
import urllib3
from requests.adapters import HTTPAdapter

http.client.HTTPConnection.debuglevel = 5
urllib3.add_stderr_logger()


class FrontingAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use SSLv3."""

    def __init__(self, fronted_domain=None, **kwargs):
        self.fronted_domain = fronted_domain
        super(FrontingAdapter, self).__init__(**kwargs)

    def send(self, request, **kwargs):
        connection_pool_kwargs = self.poolmanager.connection_pool_kw
        if self.fronted_domain:
            connection_pool_kwargs["assert_hostname"] = self.fronted_domain
        elif "assert_hostname" in connection_pool_kwargs:
            connection_pool_kwargs.pop("assert_hostname", None)
        return super(FrontingAdapter, self).send(request, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        server_hostname = None
        if self.fronted_domain:
            server_hostname = self.fronted_domain
        super(FrontingAdapter, self).init_poolmanager(server_hostname=server_hostname, *args, **kwargs)

# Based on the domain fronting example at https://digi.ninja/blog/cloudfront_example.php

s = requests.Session()
s.mount('https://', FrontingAdapter(fronted_domain="google.com"))
r = s.get("https://naver.com", headers={"Host": 'google.com'}, verify=False)
print()
print(r.content)