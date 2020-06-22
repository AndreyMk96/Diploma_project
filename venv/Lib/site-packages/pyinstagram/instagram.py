import time
import hashlib
import json
import logging

from requests_toolbelt import MultipartEncoder

from .constants import API_URL, LOGIN_EXPERIMENTS
from .response.login import LoginResponse
from .response.sync_features import SyncResponse
from .session import Session
from .signature import generate_device_id, generate_uuid, generate_signature

try:
    import httplib as http_client
except ImportError:
    import http.client as http_client

http_client.HTTPConnection.debuglevel = 1

# logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class Instagram(object):
    def __init__(self, username, password, debug=False, ig_data_path=None,
                 truncated_debug=False):
        self.session = Session()
        self.debug = debug
        self.is_logged_in = False
        self.username_id = None
        self.rank_token = None
        self.truncated_debug = truncated_debug

        self.username = None
        self.password = None
        self.uuid = None

        h = hashlib.md5()
        h.update(username.encode('utf-8'))
        h.update(password.encode('utf-8'))
        md5 = h.hexdigest()

        self.device_id = generate_device_id(md5)
        # if not ig_data_path:
        #     self.ig_data_path = ig_data_path
        #     self.custom_path = True
        # else:
        #     self.ig_data_path = os.path.join([
        #         'tmp',
        #         'ig_data_path',
        #         username
        #     ])
        #     os.makedirs(self.ig_data_path)

        self.check_settings(username)
        self.set_user(username, password)

    def check_settings(self, username):
        pass

    def set_user(self, username, password):
        self.username = username
        self.password = password
        self.uuid = generate_uuid(True)
        pass

    def login(self, force=False):
        if not self.is_logged_in or force:
            self.sync_features(True)
            self.session.send(
                url=API_URL %
                    ('si/fetch_headers/?challenge_type=signup&guid=%s' %
                     generate_uuid(False)))

            data = generate_signature(json.dumps({
                'phone_id': generate_uuid(True),
                '_csrftoken': self.session.csrftoken,
                'username': self.username,
                'guid': self.uuid,
                'device_id': self.device_id,
                'password': self.password,
                'login_attempt_count': '0',
            }))
            rv = self.session.send(API_URL % 'accounts/login/', data)

            login = LoginResponse(rv)

            self.is_logged_in = True
            self.username_id = login.pk
            self.rank_token = '%s_%s' % (self.username_id, self.uuid)

            # self.token = $match[1];
            # self.settings->set('token', $this->token);

            # self.syncFeatures();
            # self.autoCompleteUserList();
            # self.timelineFeed();
            # self.getRankedRecipients();
            # self.getRecentRecipients();
            # self.megaphoneLog();
            # self.getv2Inbox();
            # self.getRecentActivity();
            # self.getReelsTrayFeed();
            # self.explore();

            # self.get_profile_data()
            # self.get_user_tags(self.username_id)
            self.timeline_feed()
            # self.get_username_info(self.username_id)
            # self.get_pending_inbox()

    def get_user_tags(self, username_id):
        return self.session.send(
            API_URL % (
                'usertags/' + str(username_id) + '/feed/?rank_token=' + str(
                    self.rank_token) + '&ranked_content=true&',)
        )

    def get_username_info(self, username_id):
        return self.session.send(
            API_URL % ('users/' + str(username_id) + '/info/'))

    def get_pending_inbox(self):
        return self.session.send(
            API_URL % 'direct_v2/pending_inbox/?')

    def get_profile_data(self):
        return self.session.send(
            API_URL % 'accounts/current_user/?edit=true',
            generate_signature(json.dumps({
                '_uuid': self.uuid,
                '_uid': self.username_id,
                '_csrftoken': self.session.csrftoken
            })))

    def timeline_feed(self):
        return self.session.send(API_URL % ('feed/timeline/'))

    def sync_features(self, prelogin=False):
        if prelogin:
            data = json.dumps(dict(
                id=generate_uuid(True),
                experiments=LOGIN_EXPERIMENTS,
            ))
            rv = self.session.send(url=API_URL % 'qe/sync/',
                                   data=generate_signature(data))
            # import sys
            # json.dump(rv.json(), sys.stdout, indent=2)
            return SyncResponse(rv)

    def upload_photo(self, photo, caption=None, upload_id=None):
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))
        data = {
            'upload_id': upload_id,
            '_uuid': self.uuid,
            '_csrftoken': self.session.csrftoken,
            'image_compression': '{"lib_name":"jt","lib_version":"1.3.0","quality":"87"}',
            'photo': ('pending_media_%s.jpg' % upload_id, open(photo, 'rb'),
                      'application/octet-stream',
                      {'Content-Transfer-Encoding': 'binary'})
        }
        m = MultipartEncoder(data, boundary=self.uuid)
        rv = self.session.send(
            url=API_URL % "upload/photo/",
            data=m.to_string(), headers={
                'content-type': m.content_type
            })
        print(rv)
