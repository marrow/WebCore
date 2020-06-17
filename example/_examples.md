# GET /

**Basic GET Request**

As it says on the label. Utilizes the default values for arguments to the endpoint, in this case defaulting `name` to `world`.

+ Response 200 (text/html; charset=UTF-8)

        Hello world.


# GET /Alice

**Passing Name Positionally**

The `name` argument to the endpoint may be specified _positionally_, by utilizing a path element "below" the endpoint. Each otherwise unprocessed path element remaining in in the request when an endpoint is reached will be automatically utilized positionally.

+ Response 200 (text/html; charset=UTF-8)

        Hello Alice.


# GET /?name=Bob%20Dole

**Passing by Name, Query String**

The `name` argument to the endpoint alternatively be specified _by name_, as a _keyword argument_. These arguments may be sourced from several locations, such as **parsed query string arguments** ("GET" arguments), form-data encoded, or even JSON encoded "POST" bodies, and so forth.

+ Response 200 (text/html; charset=UTF-8)

        Hello Bob Dole.


# POST /

**Passing by Name, Form Body**

The `name` argument to the endpoint alternatively be specified _by name_, as a _keyword argument_. These arguments may be sourced from several locations, such as parsed query string argumets ("GET" arguments), **form-data encoded POST**, or even JSON encoded POST, and so forth.

+ Request (application/x-www-form-urlencoded; charset=utf-8)

        name=James+T.+Kirk

+ Response 200 (text/html; charset=UTF-8)

        Hello James T. Kirk.


