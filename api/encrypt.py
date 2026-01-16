import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib


def md5_encrypt(input_string):
    """
    使用MD5算法对字符串进行加密。

    参数:
    input_string (str): 需要加密的原始字符串。

    返回:
    str: 加密后的MD5哈希值，以32位小写十六进制字符串表示。
    """
    # 创建md5对象
    md5_hash = hashlib.md5()

    # 更新md5对象，可以多次调用update()方法，这里直接使用待加密的字符串转换为bytes
    md5_hash.update(input_string.encode('utf-8'))

    # 获取16进制的MD5摘要
    result = md5_hash.hexdigest()

    return result

def adjust_key_iv(key, length=24):  # 对于192位密钥，长度应为24
    """
    调整密钥和IV的长度，不足时用0x00填充，超出部分忽略。
    """
    if len(key) < 24:
        key = key.encode('utf-8')[:length] + (b'\x00' * (length - len(key.encode('utf-8'))))
    else:
        key = key.encode('utf-8')
    return key

def aes_cbc_encrypt(key, data, iv=b'\x00' * 16):
    """
    使用AES-192-CBC加密数据。
    """
    key = adjust_key_iv(key)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    result = base64.b64encode(ciphertext)

    return str(result, 'utf-8')

def aes_cbc_decrypt(key, encrypted_data, iv=b'\x00' * 16):
    """
    使用AES-192-CBC解密数据。
    """
    ciphertext = base64.b64decode(encrypted_data)
    key = adjust_key_iv(key)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    return unpad(decrypted_padded, AES.block_size).decode('utf-8')


if __name__ == '__main__':
    key = "wangnapao"
    resp_data = {
        "code": 1000,
        "msg": "校验不通过，时间已超时",
        "timestamp": time.time()
    }
    import json
    decrypt_data = aes_cbc_encrypt(key, json.dumps(resp_data))
    print(decrypt_data)

