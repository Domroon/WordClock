from time import gmtime
import socket
import struct

import urequests as requests

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
host = "ptbtime2.ptb.de"
# The NTP socket timeout can be configured at runtime by doing: ntptime.timeout = 2
timeout = 1

# Server that delivers datetime in json-Format
timezone = 'Europe/Berlin'
json_time_sever = f'https://timeapi.io/api/Time/current/zone?timeZone={timezone}'


class InternetError(Exception):
    """Raises when the Router have no connection to the Internet"""


def download_json_datetime():
    try:
        r = requests.get(json_time_sever)
        infos = r.json()
        r.close()
        return infos
    except OSError:
        raise InternetError("No response from the requested server")


def get_utc_offset(gmtime):
    return download_json_datetime()['hour'] - gmtime[3]


def download_ntp_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(timeout)
        s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]

    # 2024-01-01 00:00:00 converted to an NTP timestamp
    MIN_NTP_TIMESTAMP = 3913056000

    # Y2036 fix
    #
    # The NTP timestamp has a 32-bit count of seconds, which will wrap back
    # to zero on 7 Feb 2036 at 06:28:16.
    #
    # We know that this software was written during 2024 (or later).
    # So we know that timestamps less than MIN_NTP_TIMESTAMP are impossible.
    # So if the timestamp is less than MIN_NTP_TIMESTAMP, that probably means
    # that the NTP time wrapped at 2^32 seconds.  (Or someone set the wrong
    # time on their NTP server, but we can't really do anything about that).
    #
    # So in that case, we need to add in those extra 2^32 seconds, to get the
    # correct timestamp.
    #
    # This means that this code will work until the year 2160.  More precisely,
    # this code will not work after 7th Feb 2160 at 06:28:15.
    #
    if val < MIN_NTP_TIMESTAMP:
        val += 0x100000000

    # Convert timestamp from NTP format to our internal format

    EPOCH_YEAR = gmtime(0)[0]
    if EPOCH_YEAR == 2000:
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 3155673600
    elif EPOCH_YEAR == 1970:
        # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 2208988800
    else:
        raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

    return val - NTP_DELTA


# There's currently no timezone support in MicroPython, and the RTC is set in UTC time.
def set_rtc_time(rtc):
    t = download_ntp_time()

    tm = gmtime(t)
    utc_offset = get_utc_offset(tm)
    print("utc offset", utc_offset)
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3] + utc_offset, tm[4], tm[5], 0))


def set_timekeeper_time(timekeeper):
    t = download_ntp_time()

    tm = gmtime(t)
    utc_offset = get_utc_offset(tm)
    print("utc offset", utc_offset)
    timekeeper.set_datetime((tm[0], tm[1], tm[2], tm[3] + utc_offset, tm[4], tm[5], 0))