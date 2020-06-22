import logging

import requests

X_IG_Capabilities = '3R4='
DEVICE_SETTINTS = {
    'manufacturer': 'Xiaomi',
    'model': 'HM 1SW',
    'android_version': 18,
    'android_release': '4.3'
}
USER_AGENT = ('Instagram 9.2.0 Android ({android_version}/'
              '{android_release}; 320dpi; 720x1280; {manufacturer}; '
              '{model}; armani; qcom; en_US)'.format(**DEVICE_SETTINTS))

logger = logging.getLogger()


class InstagramException(Exception):
    pass


class Session(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'connection': 'close',
            'accept': '*/*',
            'x-ig-capabilities': '%s' % X_IG_Capabilities,
            'x-ig-connection-Type': 'WIFI',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie2': '$Version=1',
            'accept-language': 'en-US',
            'user-agent': USER_AGENT,
        })
        self.csrftoken = None

    def send(self, url, data=None, headers={}):
        method = 'get'
        if data:
            method = 'post'
        self.session.headers.update(headers)
        rv = getattr(self.session, method)(
            url=url, headers=self.session.headers, data=data)
        logger.debug(rv.json())
        if rv.status_code != 200:
            raise InstagramException()

        self.csrftoken = rv.cookies['csrftoken']
        return rv.json()
