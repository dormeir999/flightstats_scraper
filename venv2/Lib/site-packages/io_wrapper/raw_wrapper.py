"""Raw binary IO wrapper.

Implement any missing methods from \L{io.RawIOBase} for a file-like object.

@author: David Megginson
@organization: UNOCHA
@license: Public Domain
@date: Started May 2018
"""
import io

class RawIOWrapper(io.RawIOBase):
    """Wrapper for a raw (binary) IO object.
    Implements all expected methods from \L{io.RawIOBase}.
    Calls to the wrapped stream when possible.
    """

    def __init__(self, stream):
        """Set up the wrapper.
        @param stream: the raw (binary) IO object to wrap
        """
        self.stream = stream
        self._closed = False

    # from io.IOBase

    @property
    def closed(self):
        try:
            return self.stream.closed
        except AttributeError:
            return self._closed

    def close(self):
        try:
            self.stream.close()
        except AttributeError:
            self._closed = True

    def fileno(self):
        try:
            return self.stream.fileno()
        except AttributeError:
            raise io.UnsupportedOperation('File descriptor not supported')

    def flush(self):
        try:
            return self.stream.flush()
        except AttributeError:
            pass # does nothing

    def isatty(self):
        try:
            return self.stream.isatty()
        except AttributeError:
            return False

    def readable(self):
        try:
            return self.stream.readable()
        except AttributeError:
            return True # assume readable

    def readline(self, limit=None):
        try:
            return self.stream.readline(limit=limit)
        except AttributeError:
            # FIXME - honour the limit
            buffer = bytes()
            c = self.read(1)
            while len(c) > 0:
                buffer += c
                if c == b"\n":
                    break
                c = self.read(1)
            return buffer

    def readlines(self, hint=None):
        try:
            return self.stream.readlines(hint)
        except AttributeError:
            # FIXME = honour the limit
            lines = list()
            line = self.readline()
            while len(line) > 0:
                lines.append(line)
                line = self.readline()
            return lines

    def seek(self, offset, whence):
        try:
            return self.stream.seek(offset, whence)
        except AttributeError:
            raise io.UnsupportedOperation('Stream is not random-access')

    def seekable(self):
        try:
            return self.stream.seekable()
        except AttributeError:
            return False

    def tell(self):
        try:
            return self.stream.tell()
        except AttributeError:
            raise io.UnsupportedOperation('Stream is not random-access')

    def truncate(self, size=None):
        try:
            return self.stream.reader.truncate(size=size)
        except AttributeError:
            raise io.UnsupportedOperation('Stream is not random-access')

    def writeable(self):
        try:
            return self.stream.writeable()
        except AttributeError:
            return False

    def writelines(self, lines):
        try:
            return self.stream.writelines(lines)
        except AttributeError:
            for line in lines:
                self.stream.write(line)

    # from io.RawIOBase

    def read(self, size=-1):
        try:
            return self.stream.read(size)
        except AttributeError:
            raise io.UnsupportedOperation('Stream does not support reading')

    def readall(self):
        try:
            return self.stream.readall()
        except AttributeError:
            buffer = bytes()
            b = self.stream.read(4096)
            while len(b) > 0:
                buffer += b
                b = self.stream.read(4096)
            return buffer

    def readinto(self, b):
        try:
            return self.stream.readinto(b)
        except AttributeError:
            for i in range(0, len(b)):
                b1 = self.read(1)
                if len(b1) == 0:
                    return i
                else:
                    b[i] = b1[0]
            return len(b)

    def write(self, b):
        try:
            return self.stream.write(b)
        except AttributeError:
            raise io.UnsupportedOperation('Stream does not support writing')

