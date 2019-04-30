import os
import time
import random
import struct
import select
import socket
import asyncio

try:
    from . import ping_plugin
except ImportError:
    ping_plugin = None

def get_checksum(data):
    x = sum(x << 8 if i % 2 else x for i, x in enumerate(data)) & 0xFFFFFFFF
    x = (x >> 16) + (x & 0xFFFF)
    x = (x >> 16) + (x & 0xFFFF)
    return struct.pack('<H', ~x & 0xFFFF)

def ping(addr, timeout=2, number=1, data=b''):
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        payload = struct.pack('!HH', random.randrange(0, 65536), number) + data
        conn.connect((addr, 80))
        conn.sendall(b'\x08\0' + get_checksum(b'\x08\0\0\0' + payload) + payload)
    except (socket.gaierror, PermissionError) as error:
        print(error)
        return False
        
    start = time.time()

    while select.select([conn], [], [], max(0, start + timeout - time.time()))[0]:
        data = conn.recv(65536)
        if len(data) < 20 or len(data) < struct.unpack_from('!xxH', data)[0]:
            continue
        if data[20:] == b'\0\0' + get_checksum(b'\0\0\0\0' + payload) + payload:
            return True # round(time.time() - start, 6) * 1000

    return False

def async_ping(host, timeout):
    if ping_plugin:
        return ping_plugin.async_ping(host, timeout=timeout)
    raise NotImplementedError

def pingHasPermission():
  try:
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    return True
  except PermissionError:
    print('PermissionError: requires admin privileges to open raw socket')
    return False

@asyncio.coroutine
def subprocess_ping_async(addr, timeout=2, number=1, loop=None):
    if os.name == 'nt':
        create_proc = asyncio.create_subprocess_exec(
            "ping","-n",str(number),"-w","%d" % (1000*timeout), addr,
            stdout=asyncio.subprocess.PIPE,
            loop=loop)
    else:
        create_proc = asyncio.create_subprocess_exec(
            "ping","-c",str(number),"-W",str(timeout), addr,
            stdout=asyncio.subprocess.PIPE,
            loop=loop)

    proc = yield from create_proc
    #data = yield from proc.stdout.read()
    returncode = yield from proc.wait()
    return returncode == 0

@asyncio.coroutine
def tcp_port_test_async(addr, port, timeout=2, loop=None):
    try:
        available = True
        connection_future = asyncio.open_connection(addr, port, loop=loop)
        reader, writer = yield from asyncio.wait_for(connection_future, timeout, loop=loop)
        writer.close()
    except (ConnectionRefusedError, OSError):
        available = False
    except asyncio.TimeoutError:
        available = False
    return available


def test(addr, port, timeout):
    print("ping:")
    res = ping(addr, timeout)
    print("  res", res)

    @asyncio.coroutine
    def test_async(loop):
        print("subprocess_ping_async:")
        res = yield from subprocess_ping_async(addr, timeout, loop=loop)
        print("  res", res)
        
        print("tcp_port_test_async:")
        res = yield from tcp_port_test_async(addr, port, timeout, loop=loop)
        print("  res", res)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_async(loop))
    loop.close()
