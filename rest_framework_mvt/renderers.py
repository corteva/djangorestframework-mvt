from rest_framework.renderers import BaseRenderer


class BinaryRenderer(BaseRenderer):
    media_type = "application/*"
    format = "binary"
    charset = None
    render_style = "binary"

    # pylint: disable=no-self-use,unused-argument
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
