#!/usr/bin/env python

from lxml import etree
from glob import iglob
from urlparse import urlparse, urljoin
from collections import namedtuple
import hashlib

Mirror = namedtuple('Mirror', ['url', 'location'])

DESCRIPTION = 'Camp++ talks'
MIRRORS = [
    Mirror(location='de', url='https://trum.jmt.gr/camp++/'),
    Mirror(location='at', url='http://camp.noreply.org/'),
    Mirror(location='hu', url='http://static.end.re/camp++_talks/'),
        ]
OUTPUT_FILE = 'videos.metalink'

HASHES = ['md5', 'sha1', 'sha256']
BLOCKSIZE = 4096

def main():
    metalink = etree.Element('metalink', version="3.0",
            xmlns="http://www.metalinker.org/",
            generator="https://github.com/hsbp/metalink-lxml")
    etree.SubElement(metalink, 'description').text = DESCRIPTION
    files = etree.SubElement(metalink, 'files')
    for name in sorted(iglob('*.mkv')):
        node = etree.SubElement(files, 'file', name=name)
        sums = [hashlib.new(h) for h in HASHES]
        with file(name, 'rb') as f:
            block = f.read(BLOCKSIZE)
            while block:
                for s in sums:
                    s.update(block)
                block = f.read(BLOCKSIZE)
            etree.SubElement(node, 'size').text = str(f.tell())
        ver = etree.SubElement(node, 'verification')
        for algo, obj in zip(HASHES, sums):
            etree.SubElement(ver, 'hash', type=algo).text = obj.hexdigest()
        res = etree.SubElement(node, 'resources')
        for mirror in MIRRORS:
            url = urljoin(mirror.url, name)
            etree.SubElement(res, 'url', location=mirror.location,
                    type=urlparse(mirror.url).scheme).text = url
    with file(OUTPUT_FILE, 'wb') as f:
        f.write(etree.tostring(metalink, encoding='utf-8',
            pretty_print=True, xml_declaration=True))

if __name__ == '__main__':
    main()
