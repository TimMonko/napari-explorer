"""
napari-explorer widget
"""
import pathlib
from os.path import join
from typing import TYPE_CHECKING

from magicgui import magic_factory

if TYPE_CHECKING:
    import napari


file_types = ["all", ".czi", ".tif", ".png", ".jpg"]
reader_plugins = ["napari-aicsimageio", "napari"]
home_file_choices = [file.name for file in list(pathlib.Path().glob("*.*"))]


def on_init(folder_explorer):
    """Connect file directory and file extension changes to file choices.

    on_init is called each time folder_explorer creates a new widget,
      per npe2 specification.
    This is connected via widget_init param in magic_factory decorator
      on_init only accepts one input, so the input can be the only way
      to connect events.
    Perhaps in the future there will also be a way to grab the viewer
      instance without pre-defining it, such that viewer events
      can also be connected.
    """

    @folder_explorer.file_extension.changed.connect
    @folder_explorer.file_directory.changed.connect
    @folder_explorer.called.connect
    def _update_file_choices():
        if folder_explorer.file_extension.value == ["all"]:
            # get all the files in a folder that contain a .
            file_list = list(folder_explorer.file_directory.value.glob("*.*"))
        else:
            # filter out files with path.suffix according to suffixes defined
            # by the choices in file_extension
            file_list = sorted(
                filter(
                    lambda path: path.suffix
                    in folder_explorer.file_extension.value,
                    folder_explorer.file_directory.value.glob("*.*"),
                )
            )
        file_list = [file.name for file in file_list]
        folder_explorer.file_choices.choices = file_list
        print("updated file_choices")


@magic_factory(
    widget_init=on_init,
    auto_call=False,
    labels=False,
    call_button="Open Files",
    file_directory=dict(widget_type="FileEdit", mode="d"),
    file_extension=dict(widget_type="Select", choices=file_types),
    reader_plugin=dict(
        widget_type="RadioButtons", label="Reader", choices=reader_plugins
    ),
    file_choices=dict(widget_type="Select", choices=home_file_choices),
)
def folder_explorer(
    viewer: "napari.viewer.Viewer",
    file_directory=pathlib.Path(),
    file_extension="all",
    file_choices=[],
    reader_plugin="napari-aicsimageio",
):
    """Open Files

    Search a file directory and filter by file extension suffix.
    Currently bugged to not always inherit file_choices properly after
      function is called, even with event connection.
    This bug appears intrinsic to viewer.open().
    This function also forms a framework to handle any single or list
      of files as an input to a greater function.
    """
    file_locations = [
        join(str(file_directory), str(file)) for file in file_choices
    ]
    print("opening:", file_locations)
    viewer.open(path=file_locations, plugin=reader_plugin)
    return file_locations
