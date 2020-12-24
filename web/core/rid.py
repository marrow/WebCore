"""Coordination-Free Unique Identifier Generation

This module contains an ObjectID implementation independent from the `bson` package bundled with PyMongo, developed
in "clean-room" isolation based on publicly available end-use documentation. Additionally, it implements all of the
known generation algorithms, as the specification has changed over time. This is provided primarily as a mechanism
to utilize or transition older IDs on modern systems, as well as to provide an option if you prefer the guarantees
and information provided by older versions, moving forwards.

Ours being Python 3 specific is more strict about the type of string being passed. Where PyMongo's `bson.ObjectId`
permits hex-encoded binary strings, our ObjectID is strict: binary values will only be interpreted as a raw binary
ObjectID; no transformations will be applied to bytes objects.

`ObjectId` was originally[1] defined (< MongoDB 3.3) as a combination of:

* 4-byte UNIX timestamp.
* 3-byte machine identifier.
* 2-byte process ID.
* 3-byte counter with random IV on process start.

The server itself never had a complex interpretation, treating the data after the timestamp as an "arbitrary node
identifier" followed by counter. The documentation and client drivers were brought more in-line with this intended
lack of structure[2] replacing the hardware and process identifiers with literal random data initialized on process
startup. As such, the modern structure is comprised of:

* 4-byte UNIX timestamp.
* 5-byte random process identifier. ("Random value" in the docs.)
* 3-byte counter with random IV ("initialization vector", or starting point) on process start.

Additionally, the mechanism used to determine the hardware identifier has changed in the past. Initially it used a
substring segment of the hex-encoded result of hashing the value returned by `gethostname()`. For Federal Information
Processing Standard (FIPS) [3] compliance, use of MD5 was eliminated and a custom FNV implementation added. We avoid
embedding yet another hashing implementation in our own code and simply utilize the `fnv` package, if installed.
(This will be automatically installed if your own application depends upon `marrow.mongo[fips]`.) Without the library
installed, the `fips` choice will not be available.

To determine which approach is used for generation, specify the `hwid` keyword argument to the `ObjectID()`
constructor. Possibilities include:

* The string `legacy`: use the host name MD5 substring value and process ID. _Note if FIPS compliance is enabled, the
  `md5` hash will literally be unavailable for use, resulting in the inability to utilize this choice._
* The string `fips`: use the FIPS-compliant FNV hash of the host name, in combination with the current process ID.
  Requires the `fnv` package be installed.
* The string `mac`: use the hardware MAC address of the default interface as the identifier. Because a MAC address is
  one byte too large for the field, the final byte is used to XOR the prior ones.
* The string `random`: pure random bytes, the default, aliased as `modern`.
* Any 5-byte bytes value: use the given HWID explicitly.

You are permitted to add additional entries to this mapping within your own application, if desired.

Unlike the PyMongo-supplied `ObjectId` implementation, this does not use a custom `Exception` class to represent
invalid values. `TypeError` will be raised if passed a value not able to be stringified, `ValueError` if the
resulting string is not 12 binary bytes or 24 hexadecimal digits. _**Warning:** any 12-byte `bytes` value will be
accepted as-is._

Additional points of reference:

* [Implement ObjectId spec](https://jira.mongodb.org/browse/DRIVERS-499)
* [Python Driver Deprecation/Removal of MD5](https://jira.mongodb.org/browse/PYTHON-1521)
* [Java Driver "Make ObjectId conform to specification"](https://jira.mongodb.org/browse/JAVA-749)
* [ObjectID documentation should replace Process and Machine ID with 5-byte random value](https://jira.mongodb.org/browse/DOCS-11844)
* [ObjectId MachineId uses network interface names instead of mac address or something more unique](https://jira.mongodb.org/browse/JAVA-586)

### Footnotes

1. https://docs.mongodb.com/v3.2/reference/method/ObjectId/
2. https://docs.mongodb.com/v3.4/reference/method/ObjectId/
3. https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards
"""

from binascii import hexlify, unhexlify
from datetime import datetime, timedelta
from os import getpid, urandom
from random import randint
from socket import gethostname
from struct import pack, unpack
from threading import RLock
from time import time
from uuid import getnode

from ..core.typing import Union, Optional, Mapping, check_argument_types

try:
	from bson import ObjectId as _OID
	from bson.tz_util import utc

except ImportError:
	from datetime import timedelta, tzinfo
	
	class _OID: pass
	
	class FixedOffset(tzinfo):
		Z = timedelta()
		
		def __init__(self, offset, name):
			if isinstance(offset, timedelta):
				self.__offset = offset
			else:
				self.__offset = timedelta(minutes=offset)
			self.__name = name
		
		def __getinitargs__(self):
			return self.__offset, self.__name
		
		def utcoffset(self, dt):
			return self.__offset
		
		def tzname(self, dt):
			return self.__name
		
		def dst(self, dt):
			return ZERO
	
	utc = FixedOffset(0, "UTC")


# HWID calculation. This happens once, the first time this module is imported. Availability of choices depend on the
# ability to import the given hashing algorithm, e.g. `legacy` will be unavailable if `hashlib.md5` is unavailable.
# Feel free to expand upon these choices within your own application by updating `marrow.mongo.util.oid.HWID`.
# TODO: Also make this a "plugin registry", though the "plugins" are just static values or callables generating one.

_hostname: bytes = gethostname().encode()  # Utilized by the legacy HWID generation approaches.
HWID: Mapping[str,bytes] = {'random': urandom(5)}  # A mapping of abstract alias to hardware identification value, defaulting to random.
HWID['modern'] = HWID['random']  # Convenient alias as an antonym of "legacy".

mac = [int(("%012X" % getnode())[i:i+2], 16) for i in range(0, 12, 2)]
HWID['mac'] = b"".join(b"%x" % (mac[i]^mac[-1], ) for i in range(5))  # Identifier based on hardware MAc address.
del mac

try:  # This uses the old (<3.7) MD5 approach, which is not FIPS-safe despite having no cryptographic requirements.
	from hashlib import md5
	HWID['legacy'] = unhexlify(md5(_hostname).hexdigest()[:6])
except ImportError:  # pragma: no cover
	pass

try:  # A HWID variant matching MongoDB >=3.7 use of FNV-1a for FIPS compliance.
	import fnv
	_fnv = fnv.hash(_hostname, fnv.fnv_1a, bits=32)
	_fnv = (_fnv >> 24) ^ (_fnv & 0xffffff)  # XOR-fold to 24 bits.
	HWID['fips'] = pack('<I', _fnv)[:3]
except ImportError:  # pragma: no cover
	pass


class _Counter:
	"""A thread-safe atomically incrementing counter.
	
	That itertools.count is thread-safe is a byproduct of the GIL on CPython, not an intentional design decision. As a
	result it can not be relied upon, thus we implement our own with proper locking.
	"""
	
	value: int
	lock: RLock
	
	def __init__(self):
		self.value = randint(0, 2**24)
		self.lock = RLock()
	
	def __next__(self):
		with self.lock:
			self.value = (self.value + 1) % 0xFFFFFF
			value = self.value
		
		return value

_counter = _Counter()


class _Component:
	"""An object representing a component part of the larger binary ObjectID structure.
	
	This allows the definition of a range of bytes from the binary representation, with automatic extraction from the
	compound value on get, and replacement of the relevant portion of the compound value on set. Deletion will null;
	replace with zeroes.
	"""
	
	__slots__ = ('_slice', )
	
	_slice: slice
	
	def __getitem__(self, item):
		self._slice = item
		return self
	
	def __get__(self, instance, owner):
		return instance.binary[self._slice]
	
	def __set__(self, instance, value:Union[str,bytes]):
		if isinstance(value, str):
			value = unhexlify(value)
		
		start, stop, skip = self._slice.indices(12)
		l = stop - start
		
		if len(value) > l:  # Trim over-large values
			# We encode a 3-byte value as a 4-byte integer, thus need to trim it for storage.
			value = value[len(value) - l:]
		
		binary = bytearray(instance.binary)
		binary[self._slice] = value
		instance.binary = bytes(binary)
	
	def __delete__(self, instance):
		value = bytearray(instance.binary)
		value[self._slice] = b'\0' * len(range(*self._slice.indices(12)))
		instance.binary = bytes(value)


class _Numeric(_Component):
	__slots__ = ('struct', )
	
	_struct: str
	
	def __init__(self, struct='>I'):
		self.struct = struct
	
	def __get__(self, instance, owner) -> int:
		value = super().__get__(instance, owner)
		return unpack(self.struct, value)[0]
	
	def __set__(self, instance, value: int):
		assert check_argument_types()
		
		value = pack(self.struct, value)
		super().__set__(instance, value)


class _Timestamp(_Numeric):
	__slots__ = ()
	
	def __get__(self, instance, owner) -> datetime:
		value = super().__get__(instance, owner)
		return datetime.utcfromtimestamp(value).replace(tzinfo=utc)
	
	def __set__(self, instance, value:Union[int,datetime,timedelta]):
		assert check_argument_types()
		
		if not isinstance(value, int):
			if isinstance(value, timedelta):
				value = datetime.utcnow() + value
			
			value = int(datetime.timestamp(value))
		
		super().__set__(instance, value)


class ObjectID(_OID):
	__slots__ = ('binary', )
	
	_type_marker = 0x07  # BSON ObjectId
	
	time = generation_time = _Timestamp('!L')[:4]  # "time" short-hand alias provided.
	machine = _Component()[4:7]
	process = _Numeric('!H')[7:9]
	counter = sequence = _Numeric('!I')[9:]  # "sequence" alias provided.
	
	hwid = _Component()[4:9]  # Compound of machine + process, used esp. in later versions as random.
	
	def __init__(self, value:Optional[Union[str,bytes,_OID,datetime,timedelta]]=None, hwid='random'):
		assert check_argument_types()
		
		self.binary = b'\x00' * 12
		
		if isinstance(value, (datetime, timedelta)):
			self.binary = self.from_datetime(value).binary
		
		elif value:
			self.parse(value)
		
		else:
			self.generate(hwid)
	
	@classmethod
	def from_datetime(ObjectID, when:Union[datetime,timedelta]):
		"""Construct a mock ObjectID whose only populated field is a specific generation time.
		
		This is useful for performing range queries (e.g. records constructed after X `datetime`). To enhance such use
		this reimplementation allows you to pass an explicit `datetime` instance, or a `timedelta` relative to now.
		
		All dates are normalized to UTC and are only second accurate.
		"""
		
		assert check_argument_types()
		
		if isinstance(when, timedelta):  # If provided a relative moment, assume it's relative to now.
			when = datetime.utcnow() + when
		
		if not when.tzinfo:
			when = when.replace(tzinfo=utc)
		
		if when.utcoffset():  # Normalize to UTC.
			when = when - when.utcoffset()
		
		ts = int(datetime.timestamp(when))  # Throw away microseconds - the decimal component of the float.
		oid = pack('>I', ts) + b"\0\0\0\0\0\0\0\0"
		
		return ObjectID(oid)
	
	@classmethod
	def is_valid(ObjectID, oid):
		"""Identify if the given identifier will parse successfully as an ObjectID."""
		
		try:
			ObjectID(oid)
		except (TypeError, ValueError):
			return False
		
		return True
	
	def parse(self, value):
		if isinstance(value, bytes):
			value = hexlify(value).decode()
		
		value = str(value)  # Casts bson.ObjectId as well.
		
		if len(value) != 24:
			raise ValueError("ObjectID must be a 12-byte binary value or 24-character hexadecimal string.")
		
		self.binary = unhexlify(value)
	
	def generate(self, hwid='random'):
		self.time = int(time())  # 4 byte timestamp.
		
		if hwid in ('legacy', 'fips'):  # Machine + process identification.
			self.machine = HWID[hwid]
			self.process = getpid() % 0xFFFF  # Can't be precomputed and included in HWID as Python may fork().
		
		elif isinstance(hwid, bytes):  # 5-byte explicit value
			if len(hwid) != 5:
				raise ValueError(f"Binary hardware ID must have exact length: 5 bytes, not {len(hwid)}.")
			
			self.hwid = hwid
		
		else:  # 5-byte identifier from catalog.
			self.hwid = HWID[hwid]
		
		# 3 bytes incremental counter, random IV on process start.
		self.counter = next(_counter)
	
	@property
	def _ObjectId__id(self):
		"""Provide a PyMongo BSON ObjectId-specific "private" (mangled) attribute.
		
		We have to include this, since the BSON C code explicitly pulls from the private interface instead of using
		public ones such as string- or bytes-casting. It's understandable, if unfortunate extremely tight coupling.
		
		Ref: `case 7` of `_write_element_to_buffer` from:
			https://github.com/mongodb/mongo-python-driver/blob/master/bson/_cbsonmodule.c
		
		Ref: https://jira.mongodb.org/browse/PYTHON-1843
		"""
		return self.binary
	
	def __getstate__(self):
		"""Return a value suitable for pickle serialization."""
		return self.binary
	
	def __setstate__(self, value):
		"""Restore state after pickle deserialization."""
		self.binary = value
	
	def __str__(self):
		return hexlify(self.binary).decode()
	
	def __bytes__(self):
		return self.binary
	
	def __repr__(self):
		return f"{self.__class__.__name__}('{self}', generated='{self.generation_time.isoformat()}')"
	
	def __eq__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary == other.binary
	
	def __ne__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary != other.binary
	
	def __lt__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary < other.binary
	
	def __le__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary <= other.binary
	
	def __gt__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary > other.binary
	
	def __ge__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary >= other.binary
	
	def __hash__(self):
		"""Retrieve a hash value for this identifier to allow it to be used as a key in mappings."""
		return hash(self.binary)
