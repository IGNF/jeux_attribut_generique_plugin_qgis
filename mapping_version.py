from qgis.PyQt.QtCore import Qt,QSettings,QEvent
from qgis.PyQt.QtWidgets import QMessageBox,QFrame,QDialog

# QT6
try :
    # Dialog = Qt.WindowType.Dialog
    Accepted = QDialog.DialogCode.Accepted
    Window = Qt.WindowType.Window
    ToolTip = Qt.WindowType.ToolTip
    FramelessWindowHint = Qt.WindowType.FramelessWindowHint
    WindowCloseButtonHint = Qt.WindowType.WindowCloseButtonHint
    # WindowTitleHint = Qt.WindowType.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
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
    LeftButton = Qt.MouseButton.LeftButton
    NoContextMenu = Qt.ContextMenuPolicy.NoContextMenu
    Warning = QMessageBox.Icon.Warning
    Information = QMessageBox.Icon.Information
    Ok = QMessageBox.StandardButton.Ok
    RichText = Qt.TextFormat.RichText
    SolidPattern = Qt.BrushStyle.SolidPattern
    CaseInsensitive = Qt.CaseSensitivity.CaseInsensitive
    WA_TransparentForMouseEvents = Qt.WidgetAttribute.WA_TransparentForMouseEvents
    NativeFormat = QSettings.Format.NativeFormat
    UserScope = QSettings.Scope.UserScope
    HLine = QFrame.Shape.HLine
    Sunken = QFrame.Shadow.Sunken
    MouseButtonPress = QEvent.Type.MouseButtonPress
    MouseMove = QEvent.Type.MouseMove
    MouseButtonRelease = QEvent.Type.MouseButtonRelease

# QT5
except AttributeError:
    # Dialog = Qt.Dialog
    Accepted = QDialog.Accepted
    Window = Qt.Window
    ToolTip = Qt.ToolTip
    FramelessWindowHint = Qt.FramelessWindowHint
    WindowCloseButtonHint = Qt.WindowCloseButtonHint
    # WindowTitleHint = Qt.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowStaysOnTopHint
    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
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
    LeftButton = Qt.LeftButton
    NoContextMenu = Qt.NoContextMenu
    Warning = QMessageBox.Warning
    Information = QMessageBox.Information
    Ok = QMessageBox.Ok
    RichText = Qt.RichText
    SolidPattern = Qt.SolidPattern
    CaseInsensitive = Qt.CaseInsensitive
    WA_TransparentForMouseEvents = Qt.WA_TransparentForMouseEvents
    NativeFormat = QSettings.NativeFormat
    UserScope = QSettings.UserScope
    HLine = QFrame.HLine
    Sunken = QFrame.Sunken
    MouseButtonPress = QEvent.MouseButtonPress
    MouseMove = QEvent.MouseMove
    MouseButtonRelease = QEvent.MouseButtonRelease
