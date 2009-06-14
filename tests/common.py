import web.core


class PlainController(web.core.Controller):
    def __before__(self, *parts, **data):
        web.core.response.content_type = "text/plain"
        return super(PlainController, self).__before__(*parts, **data)
