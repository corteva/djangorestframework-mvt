from rest_framework_mvt.renderers import BinaryRenderer


def test_BinaryRenderer__returns_data():
    binary_renderer = BinaryRenderer()

    data = binary_renderer.render(b"mytest")

    assert data == b"mytest"
