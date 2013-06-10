import colors
import re


def write(format, *values):
    """Formats string and replaces color tags."""
    print re.sub('\[(.+?)](.+?)\[/.+?]', lambda m: getattr(colors, m.groups()[0])(m.groups()[1]), format % values)