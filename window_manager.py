from qgis.PyQt.QtCore import QPoint,QSettings
from qgis.PyQt.QtWidgets import QApplication
from .constante import *


def sauve_position_dial(dlg):
    settings = QSettings(QSettings.Format.NativeFormat, QSettings.Scope.UserScope, "IGN", TITRE)
    settings.setValue("position", dlg.pos())
    settings.setValue("visible", dlg.isVisible())

def restore_position_dial(dlg):
    settings = QSettings(QSettings.Format.NativeFormat, QSettings.Scope.UserScope, "IGN", TITRE)
    pos = settings.value("position", type=QPoint)
    if not pos:
        return
    screens = QApplication.screens()
    multi = len(screens) > 1
    # Vérifie si la position est sur un des écrans
    on_screen = any(screen.geometry().contains(pos) for screen in screens)
    if on_screen:
        dlg.move(pos)

    else:
        # Si un seul écran → replacer en haut-gauche
        if not multi:
            dlg.move(QPoint(0, 0))
        else:
            # Multi-écran mais position invalide → centrer sur écran principal
            primary = QApplication.primaryScreen().geometry()
            center = primary.center()
            dlg.move(center - dlg.rect().center())

