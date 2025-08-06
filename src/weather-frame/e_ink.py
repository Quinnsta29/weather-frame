import argparse
import pathlib
import sys

from PIL import Image

from inky.auto import auto

inky = auto(ask_user=True, verbose=True)
saturation = 0.5

def display_screenshot(filepath: pathlib.Path, saturation: float = 0.5):
    """Display a screenshot on the Inky Impression display.

    Args:
        filepath (pathlib.Path): Path to the screenshot file.
    """
    inky = auto(ask_user=True, verbose=True)

    image = Image.open(filepath)
    resizedimage = image.resize(inky.resolution)

    try:
        inky.set_image(resizedimage, saturation=saturation)
    except TypeError:
        inky.set_image(resizedimage)

    inky.show()
