"""
Icon system for OpCore Simplify GUI using qfluentwidgets
qfluentwidgets provides FluentIcon enum with built-in icons
"""

from qfluentwidgets import FluentIcon

# Icon mapping for backward compatibility


class Icons:
    """Icon provider using qfluentwidgets FluentIcon"""

    @staticmethod
    def get_icon(name):
        """Get FluentIcon by name"""
        icon_map = {
            'upload': FluentIcon.FOLDER_ADD,
            'settings': FluentIcon.SETTING,
            'search': FluentIcon.SEARCH,
            'wrench': FluentIcon.CONSTRACT,
            'hammer': FluentIcon.DEVELOPER_TOOLS,
            'wifi': FluentIcon.WIFI,
            'clipboard': FluentIcon.DOCUMENT,
            'check': FluentIcon.ACCEPT,
            'cross': FluentIcon.CLOSE,
            'warning': FluentIcon.WARNING,
            'info': FluentIcon.INFO,
            'lightning': FluentIcon.LIGHTNING,
            'folder': FluentIcon.FOLDER,
            'save': FluentIcon.SAVE,
            'download': FluentIcon.DOWNLOAD,
            'refresh': FluentIcon.SYNC,
            'delete': FluentIcon.DELETE,
            'add': FluentIcon.ADD,
            'remove': FluentIcon.REMOVE,
            'edit': FluentIcon.EDIT,
            'copy': FluentIcon.COPY,
            'cut': FluentIcon.CUT,
            'paste': FluentIcon.PASTE,
        }
        return icon_map.get(name, FluentIcon.INFO)
