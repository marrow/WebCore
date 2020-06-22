FORMAT: 1A

# Basic Endpoint Example

A basic *endpoint* is essentially just a function:

```python
def greet(context, name:str="world") -> str:
	return f"Hello {name}."
```

As a modern Python 3 citizen, it's properly type annotated. To try to be at least somewhat useful, it accepts an argument, and returns a [formatted string](https://docs.python.org/3/library/string.html#format-string-syntax) (*variable expansion* via a [*formatted string literal*](https://docs.python.org/3/reference/lexical_analysis.html#f-strings); [see also](https://pyformat.info)) inserting the submitted value into the archetypical phrase and returning the result of that operation.

This illustrates an essential point: you can write a Python API first, and then *expose* it to the internet using WebCore. WebCore is very flexible in how it *collects* arguments for, then *invokes* your endpoint, processes the returned value, finally applying the result to the response using a *view*.

In all of these example cases, the mime-type is being defined by the "Unicode string" *view*—`BaseExtension.render_text`—not detecting any HTML in the returned text.  If it did detect HTML—likely tags, HTML entities—the mime-type would be defined as `text/html`, unless overridden prior to return. For more complete _negotiation_ of the returned content-type, please reference the `SerializationExtension`.

> **Note:** If attempting to return XML as text, rather than returning an ElementTree object, for example, ensure you apply the correct mime-type before returning, or your XML may be delivered as HTML.


# Group Example Invocations

There are a few ways a given endpoint can be invoked, after being discovered through *dispatch*—the process of resolving a requested URI to some object it represents. In our example case above there is essentially no dispatch step; regardless of the requested URI the function passed as the application root can not be "descended past", and will always be utilized to answer the request.


## Basic GET Request [/]

### Retrieve the Default Response [GET]
With no arguments specified through any mechanism, the default value assigned in the code for `name`—`world`—will be utilized.

+ Request Plain Text Message

	+ Headers

		Accept: text/plain

+ Response 200 (text/plain; charset=UTF-8)

		Hello world.


## Passing Name Positionally [/Alice]
The `name` argument to the endpoint may be specified *positionally*, by utilizing a path element "below" the endpoint. Each otherwise unprocessed path element remaining in in the request when an endpoint is reached will be automatically utilized positionally.

+ Request Plain Text Message

	+ Headers

		Accept: text/plain

+ Response 200 (text/plain; charset=UTF-8)

		Hello Alice.


## Passing by Name, Query String [/?name=Bob+Dole]

The `name` argument to the endpoint might alternatively be specified *by name*, as a *keyword argument*. These arguments may be sourced from several locations, such as **parsed query string arguments** ("GET" arguments), form-data encoded, or even JSON encoded "POST" bodies, and so forth.

+ Request Plain Text Message

	+ Headers

		Accept: text/plain

+ Response 200 (text/plain; charset=UTF-8)

		Hello Bob Dole.


## Passing by Name, Form Body [/]

The `name` argument to the endpoint alternatively be specified *by name*, as a *keyword argument*. These arguments may be sourced from several locations, such as parsed query string argumets ("GET" arguments), **form-data encoded POST**, or even JSON encoded POST, and so forth.

+ Request (application/x-www-form-urlencoded; charset=utf-8)

	+ Headers

		Accept: text/plain

	+ Body

		name=James+T.+Kirk

+ Response 200 (text/plain; charset=UTF-8)

		Hello James T. Kirk.


