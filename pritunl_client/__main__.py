import optparse
import sys
import os
import re
import subprocess
import signal
import time
import hashlib

def client():
    import pritunl_client.interface
    parser = optparse.OptionParser()
    parser.add_option('--version', action='store_true', help='Print version')
    (options, args) = parser.parse_args()

    if options.version:
        print '%s v%s' % (pritunl.__title__, pritunl.__version__)
        sys.exit(0)

    interface = pritunl_client.interface.Interface()
    interface.main()

def pk():
    if sys.argv[1] in ('start', 'autostart'):
        regex = r'(?:/pritunl_client/profiles/[a-z0-9]+\.ovpn)$'
        if not re.search(regex, sys.argv[2]):
            raise ValueError('Profile must be in home directory')
        if sys.argv[1] == 'autostart':
            with open(sys.argv[2], 'r') as profile_file:
                profile_hash = hashlib.sha1(profile_file.read()).hexdigest()
            profile_hash_path = os.path.join(os.path.abspath(os.sep),
                'etc', 'pritunl_client', profile_hash)
            if not os.path.exists(profile_hash_path):
                raise ValueError('Profile not authorized to autostart')
        process = subprocess.Popen(['openvpn', sys.argv[2]])
        def sig_handler(signum, frame):
            process.send_signal(signum)
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)
        sys.exit(process.wait())
    elif sys.argv[1] == 'stop':
        regex = r'(?:/pritunl_client/profiles/[a-z0-9]+\.ovpn)$'
        with open('/proc/%s/cmdline' % int(sys.argv[2]), 'r') as cmdline_file:
            cmdline = cmdline_file.read().strip().strip('\x00')
            if not re.search(regex, cmdline):
                raise ValueError('Not a pritunl client process')
        os.kill(int(sys.argv[2]), signal.SIGTERM)
        for i in xrange(int(5 / 0.1)):
            time.sleep(0.1)
            if not os.path.exists('/proc/%s' % int(sys.argv[2])):
                break
            os.kill(int(sys.argv[2]), signal.SIGTERM)
    elif sys.argv[1] == 'set_autostart':
        regex = r'(?:/pritunl_client/profiles/[a-z0-9]+\.ovpn)$'
        if not re.search(regex, sys.argv[2]):
            raise ValueError('Profile must be in home directory')
        with open(sys.argv[2], 'r') as profile_file:
            profile_hash = hashlib.sha1(profile_file.read()).hexdigest()
        profile_hash_path = os.path.join(os.path.abspath(os.sep),
            'etc', 'pritunl_client', profile_hash)
        with open(profile_hash_path, 'w') as profile_hash_file:
            pass
    elif sys.argv[1] == 'clear_autostart':
        profile_hash_path = os.path.join(os.path.abspath(os.sep),
            'etc', 'pritunl_client', sys.argv[2])
        if os.path.exists(profile_hash_path):
            os.remove(profile_hash_path)
