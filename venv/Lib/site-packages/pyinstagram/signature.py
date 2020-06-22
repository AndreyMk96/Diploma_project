import hashlib

import uuid

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

import hmac

IG_SIG_KEY = '012a54f51c49aa8c5c322416ab1410909add32c966bbaa0fe3dc58ac43fd7ede'
SIG_KEY_VERSION = '4'


def generate_signature(data):
    return 'ig_sig_key_version=%s&signed_body=%s.%s' % (
        SIG_KEY_VERSION,
        hmac.new(IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'),
                 hashlib.sha256).hexdigest(),
        quote(data)
    )


def generate_uuid(type):
    generated_uuid = str(uuid.uuid4())
    if (type):
        return generated_uuid
    else:
        return generated_uuid.replace('-', '')


def generate_device_id(seed):
    volatile_seed = "12345"
    m = hashlib.md5()
    m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
    return 'android-' + m.hexdigest()[:16]
