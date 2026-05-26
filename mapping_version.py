from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTabBar,QMessageBox,QAbstractItemView,QListWidget

# QT6
try :
    # Dialog = Qt.WindowType.Dialog
    Window = Qt.WindowType.Window
    WindowCloseButtonHint = Qt.WindowType.WindowCloseButtonHint
    # WindowTitleHint = Qt.WindowType.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint
    # Checked = Qt.CheckState.Checked
    # Unchecked = Qt.CheckState.Unchecked
    # ItemIsEnabled = Qt.ItemFlag.ItemIsEnabled
    # ItemIsUserCheckable = Qt.ItemFlag.ItemIsUserCheckable
    # MatchExactly = Qt.MatchFlag.MatchExactly
    # RightSide = QTabBar.ButtonPosition.RightSide
    # LeftSide = QTabBar.ButtonPosition.LeftSide
    # Warning = QMessageBox.Icon.Warning
    # YesRole = QMessageBox.ButtonRole.YesRole
    # AcceptRole = QMessageBox.ButtonRole.AcceptRole
    # NoSelection = QAbstractItemView.SelectionMode.NoSelection
    NoFocus = Qt.FocusPolicy.NoFocus
    DisplayRole = Qt.ItemDataRole.DisplayRole
    BackgroundRole = Qt.ItemDataRole.BackgroundRole
    RightButton = Qt.MouseButton.RightButton
    NoContextMenu = Qt.ContextMenuPolicy.NoContextMenu
# QT5
except :
    # Dialog = Qt.Dialog
    Window = Qt.Window
    WindowCloseButtonHint = Qt.WindowCloseButtonHint
    # WindowTitleHint = Qt.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowStaysOnTopHint
    # Checked = Qt.Checked
    # Unchecked = Qt.Unchecked
    # ItemIsEnabled = Qt.ItemIsEnabled
    # ItemIsUserCheckable = Qt.ItemIsUserCheckable
    # MatchExactly = Qt.MatchFlag.MatchExactly
    # RightSide = QTabBar.RightSide
    # LeftSide = QTabBar.LeftSide
    # Warning = QMessageBox.Warning
    # YesRole = QMessageBox.YesRole
    # AcceptRole = QMessageBox.AcceptRole
    # NoSelection = QListWidget.NoSelection
    NoFocus = Qt.NoFocus
    DisplayRole = Qt.DisplayRole
    BackgroundRole = Qt.BackgroundRole
    RightButton = Qt.RightButton
    NoContextMenu = Qt.NoContextMenu