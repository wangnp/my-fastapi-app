import json
import time
import encrypt


class Response:
    def __init__(self, code, msg, data=None):
        self.code = code
        self.msg = msg
        self.data = data if data else None

    @classmethod
    def success(cls, code=0, msg='success', data=None):
        return cls(code, msg, data).to_dict()

    @classmethod
    def error(cls, code=-1, msg='error', data=None):
        return cls(code, msg, data).to_dict()

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }

    def json_response(self):
        return self.to_dict()


class ApiResponse:
    def __init__(self, key, code, msg, data=None):
        self.key = key
        self.code = code
        self.msg = msg
        self.data = data
        self.timestamp = int(time.time())

    @classmethod
    def success(cls, code=0, msg='success', data=None):
        return cls(code, msg, data).to_dict()

    @classmethod
    def error(cls, code=-1, msg='error', data=None):
        return cls(code, msg, data).to_dict()

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }

    @classmethod
    def success_encrypt(cls, key, code, msg, data=None):
        return cls(key, code, msg, data).to_encrypt_dict()

    @classmethod
    def error_encrypt(cls, key, code, msg, data=None):
        return cls(key, code, msg, data).to_encrypt_dict()

    def to_encrypt_dict(self):
        a = {
            "timestamp": self.timestamp,
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }
        a = encrypt.aes_cbc_encrypt(self.key, json.dumps(a))
        b = encrypt.md5_encrypt(a + self.key)
        return {
            "a": a,
            "b": b
        }

