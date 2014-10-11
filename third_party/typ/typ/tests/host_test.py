# Copyright 2014 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import unittest

from typ.host import Host


class TestHost(unittest.TestCase):

    def host(self):
        return Host()

    def test_files(self):
        h = self.host()
        orig_cwd = h.getcwd()
        try:
            now = h.time()

            # TODO: MacOS does goofy things with temp dirs by default, so
            # we can't compare for equality. Figure out how to get the normpath
            # from mkdtemp
            dirpath = h.mkdtemp(suffix='host_test')
            self.assertTrue(h.isdir(dirpath))
            h.chdir(dirpath)
            self.assertIn(dirpath, h.getcwd())

            h.maybe_mkdir('bar')
            self.assertTrue(h.exists(dirpath, 'bar'))
            self.assertTrue(h.isdir(dirpath, 'bar'))
            self.assertFalse(h.isfile(dirpath, 'bar'))

            bar_path = h.join(dirpath, 'bar')
            self.assertEqual(dirpath, h.dirname(bar_path))

            h.write_text_file('bar/foo.txt', 'foo')
            self.assertTrue(h.exists('bar', 'foo.txt'))
            self.assertEqual(h.read_text_file('bar/foo.txt'), 'foo')
            self.assertTrue(h.exists(dirpath, 'bar', 'foo.txt'))
            self.assertTrue(h.isfile(dirpath, 'bar', 'foo.txt'))
            self.assertFalse(h.isdir(dirpath, 'bar', 'foo.txt'))

            h.write_binary_file('binfile', b'bin contents')
            self.assertEqual(h.read_binary_file('binfile'),
                             b'bin contents')

            self.assertEqual(sorted(h.files_under(dirpath)),
                             ['bar' + h.sep + 'foo.txt', 'binfile'])

            mtime = h.mtime(dirpath, 'bar', 'foo.txt')
            self.assertGreaterEqual(now, mtime - 0.1)
            h.remove(dirpath, 'bar', 'foo.txt')
            self.assertFalse(h.exists(dirpath, 'bar', 'foo.txt'))
            self.assertFalse(h.isfile(dirpath, 'bar', 'foo.txt'))

            h.chdir(orig_cwd)
            h.rmtree(dirpath)
            self.assertFalse(h.exists(dirpath))
            self.assertFalse(h.isdir(dirpath))
        finally:
            h.chdir(orig_cwd)

    def test_terminal_width(self):
        h = self.host()
        self.assertGreaterEqual(h.terminal_width(), 0)

    def test_for_mp(self):
        h = self.host()
        self.assertEqual(h.for_mp(), None)

    def test_cpu_count(self):
        h = self.host()
        self.assertGreaterEqual(h.cpu_count(), 1)

    def test_getenv(self):
        h = self.host()
        self.assertNotEqual(h.getenv('PATH', ''), None)

    def test_basename(self):
        h = self.host()
        self.assertEqual(h.basename('foo.txt'), 'foo.txt')
        self.assertEqual(h.basename('foo/bar.txt'), 'bar.txt')

    def test_splitext(self):
        h = self.host()
        self.assertEqual(h.splitext('foo'), ('foo', ''))
        self.assertEqual(h.splitext('foo.txt'), ('foo', '.txt'))
        self.assertEqual(h.splitext('foo/bar'), ('foo/bar', ''))
        self.assertEqual(h.splitext('foo/bar.txt'), ('foo/bar', '.txt'))

    def test_print(self):
        h = self.host()

        class FakeStream(object):

            def __init__(self):
                self.contents = None
                self.flush_called = False

            def write(self, m):
                self.contents = m

            def flush(self):
                self.flush_called = True

        s = FakeStream()
        h.print_('hello', stream=s)
        self.assertEqual(s.contents, 'hello\n')
        self.assertTrue(s.flush_called)

        s = FakeStream()
        h.stdout = s
        h.print_('hello')
        self.assertEqual(s.contents, 'hello\n')

        s = FakeStream()
        h.stdout = s
        h.print_('hello', '')
        self.assertEqual(s.contents, 'hello')

    def test_call(self):
        h = self.host()
        ret, out, err = h.call(
            [h.python_interpreter,
             '-c', 'import sys; sys.stdout.write(sys.stdin.read())'],
            stdin='foo', env={})
        self.assertEqual(ret, 0)
        self.assertEqual(out, 'foo')
        self.assertEqual(err, '')

        ret, out, err = h.call(
            [h.python_interpreter,
             '-c', 'import sys; sys.stderr.write("err\\n")'])
        self.assertEqual(ret, 0)
        self.assertEqual(out, '')
        self.assertIn(err, ('err\n', 'err\r\n'))

    def test_add_to_path(self):
        orig_sys_path = sys.path[:]
        try:
            h = self.host()
            h.add_to_path(sys.path[-1])
            self.assertEqual(sys.path, orig_sys_path)

            dirpath = h.mkdtemp()
            h.add_to_path(dirpath)
            self.assertNotEqual(sys.path, orig_sys_path)
        finally:
            sys.path = orig_sys_path