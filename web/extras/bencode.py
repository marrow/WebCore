# encoding: utf-8
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
#

"""Safe message serializers for use by the underlying RPC mechanism."""


__all__ = ['CodecError', 'EncodeError', 'DecodeError', 'Encoding', 'ChunkedEncoder', 'Bencode', 'EnhancedBencode']



class CodecError(Exception):
    """Useful superclass to group all codec-related errors."""

class EncodeError(CodecError):
    """Raised by C{Encoding} implementations if encode fails."""

class DecodeError(CodecError):
    """Raised by C{Encoding} implementations if decode fails."""


class Encoding(object):
    """Interface for RPC message encoders/decoders.
    
    All encoding implementations used with this library should inherit and implement this.
    """
    
    def encode(self, data):
        """Encode data.
        
        @param data: The data to encode.  Must, at a minimum, implement encoding of C{str}, C{int}, and C{long} values.
        
        @return: The encoded data.
        @rtype: str
        """
        raise NotImplementedError
    
    def decode(self, data):
        """Decode data.
        
        @param data: The data (byte string) to decode.
        @type data: str
        
        @return: The decoded data (in its correct type).
        """
        raise NotImplementedError


class ChunkedEncoder(Encoding):
    """A mix-in class to easily chunked encoders."""
    
    def encode(self, data):
        try:
            return getattr(self, 'encode_' + type(data).__name__)(data)
        
        except AttributeError:
            raise EncodeError, "Unable to encode a chunk of type '%s'." % (type(data), )


class Bencode(ChunkedEncoder):
    """Implementation of the bencode algorithm used by Bittorrent.
    
    See: http://en.wikipedia.org/wiki/Bencode
    
    Suported Values: C{str}, C{int}, C{long}, C{dict}, C{list}
    """
    
    def decode(self, data):
        length = len(data)
        
        if length == 0: raise DecodeError, "Can not decode an empty string."
        
        data, processed = self._decode(data)
        
        if processed != length: raise DecodeError, "Did not fully decode input. %d of %d processed, %d bytes remaining." % (processed, length, length - processed)
        
        return data
    
    def _decode(self, data, offset=0):
        signature = data[offset : offset + 1]
        
        if hasattr(self, 'decode_' + signature):
            return getattr(self, 'decode_' + signature)(data, offset + 1)
        
        if signature.isdigit():
            return self.decode_str(data, offset)
        
        raise DecodeError, "Unable to decode unknown signature '%s'." % (signature, )
    
    def encode_int(self, data):
        return 'i%de' % (data, )
    
    encode_long = encode_int
    encode_bool = encode_int
    
    def decode_i(self, data, o):
        index = data.index('e', o)
        return int(data[o:index]), index + 1
    
    def encode_str(self, data):
        return '%d:%s' % (len(data), data)
    
    def decode_str(self, data, o):
        index = data.index(':', o)
        length = int(data[o:index])
        offset = index + 1
        return data[offset : offset + length], offset + length
    
    def encode_list(self, data):
        return 'l%se' % (''.join([self.encode(item) for item in data]), )
    
    encode_tuple = encode_list
    
    def decode_l(self, data, o):
        offset = o
        values = []
        
        while data[offset] != 'e':
            value, offset = self._decode(data, offset)
            values.append(value)
        
        return values, offset + 1
    
    def encode_dict(self, data):    return 'd%se' % (''.join([(self.encode(key) + self.encode(data[key])) for key in sorted(data.keys())]), )
    def decode_d(self, data, o):
        offset = o
        values = {}
        
        while data[offset] != 'e':
            key, offset = self._decode(data, offset)
            value, offset = self._decode(data, offset)
            values[key] = value
        
        return values, offset + 1


class EnhancedBencode(Bencode):
    """Implementation of a Bencode-based algorithm.
    
    Suported Values: C{str}, C{int}, C{long}, C{dict}, C{list}, C{float}, C{None}, C{tuple}, C{set}, C{unicode}
    
    @note: This algorithm differs from the "official" Bencode algorithm in that it can encode/decode additional data types.
    """
    
    def encode_float(self, data):
        return 'f%fe' % (data, )
    
    def decode_f(self, data, o):
        index = data.index('e', o)
        return float(data[o:index]), index + 1
    
    def encode_NoneType(self, data):
        return 'n'
    
    def decode_n(self, data, o):
        return None, o
    
    def encode_tuple(self, data):
        return 't%se' % (''.join([self.encode(item) for item in data]), )
    
    def decode_t(self, data, o):
        offset = o
        values = []
        
        while data[offset] != 'e':
            value, offset = self._decode(data, offset)
            values.append(value)
        
        return tuple(values), offset + 1
    
    def encode_set(self, data):
        return 's%se' % (''.join([self.encode(item) for item in data]), )
    
    def decode_s(self, data, o):
        offset = o
        values = []
        
        while data[offset] != 'e':
            value, offset = self._decode(data, offset)
            values.append(value)
        
        return set(values), offset + 1
    
    def encode_unicode(self, data):
        encoded = data.encode('utf-8')
        return 'u%d:%s' % (len(encoded), encoded)
    
    def decode_u(self, data, o):
        index = data.index(':', o)
        length = int(data[o:index])
        offset = index + 1
        return data[offset : offset + length].decode('utf-8'), offset + length
