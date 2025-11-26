import json
import os.path
import shutil

from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QFileDialog, QPushButton, QDateTimeEdit, QDialog, \
    QGridLayout, QTextEdit
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import Qt
from qgis._core import QgsProject

from .constante import *
import subprocess


def importer_json(dlg):
    fichier_source, _ = QFileDialog.getOpenFileNames(dlg,
        "Choisissez le fichier à importer : config.json et/ou param.json",
        "",
        "Fichiers JSON (*.json);"
    )
    if not fichier_source:
        QMessageBox.warning(dlg, "Annulé", "Aucun fichier sélectionné.")
        return

    fic_cible = {"config.json": PATHJSON,"param.json": PATHJSONPARAM}
    nb_remplaces = 0
    erreurs = []
    for fichier in fichier_source:
        nom_fichier = os.path.basename(fichier)
        if nom_fichier in fic_cible:
            cible = fic_cible[nom_fichier]
            try:
                shutil.copy(fichier, cible)
                nb_remplaces += 1
            except Exception as e:
                erreurs.append(f"{nom_fichier} → {str(e)}")
        else:
            erreurs.append(f"{nom_fichier} : fichier non reconnu, ignoré.")

    if erreurs:
        msg = "Certaines erreurs sont survenues :\n" + "\n".join(erreurs)
        QMessageBox.warning(dlg, "Import partiel", msg)
    else:
        QMessageBox.information(
            dlg,
            "Succès",
            f"{nb_remplaces} fichier(s) remplacé(s) avec succès."
        )


def exporter_json(dlg):
    dossier = QFileDialog.getExistingDirectory(dlg,"Choisissez un dossier de destination")
    if dossier:
        shutil.copy(PATHJSON, dossier)
        shutil.copy(PATHJSONPARAM, dossier)
    else:
        # QTimer.singleShot(0, dossier)
        QMessageBox.warning(dlg, "Annulé", "Aucun dossier sélectionné.")

def loadjson(layer_name):
    filtre_layer = {}
    try:
        if os.path.exists(PATHJSON):
            with open(PATHJSON, "r", encoding="utf-8") as f:
                filtres = json.load(f)
                filtre_layer = filtres.get(layer_name, {})
    except Exception as e:
        print(f"Erreur lecture JSON : {e}")
        filtre_layer = {}
    return filtre_layer

# retourne tous les champs sans exceptions
def get_champs(layer):
    # dictionnaire (cle = type , values = valeur)
    # dico_type_champs = {}
    dico_type_champs = {}
    for field in layer.fields():
        index = layer.fields().indexOf(field.name())
        type_champ = layer.editorWidgetSetup(index).type()
        if type_champ not in dico_type_champs:
            dico_type_champs[type_champ] = []
        if field.name() not in CHAMP_NON_PRIS_EN_COMPTE:
            dico_type_champs[type_champ].append(field.name())
    return dico_type_champs

# retourne les valeurs possibles d'un champ
def get_valeur(layer,champ):
    if champ == "":
        return
    layer_field = layer.fields().field(champ)
    # Vérifier le type d’éditeur liste de dico (troncon_hydro) ou dico (autre)
    editor_setup = layer_field.editorWidgetSetup()
    valeurs_possibles = []
    for v in editor_setup.config().values():
        # cas de liste de dictionnaire → on dépile
        if isinstance(v, dict):
            valeurs_possibles.extend(v.values())  # récupérer les vrais libellés
        # Cas où c'est une liste : cf. tronçon hydro
        elif isinstance(v, list):
            # Cas d’une liste → on ajoute chaque élément
            for elem in v:
                if isinstance(elem, dict):
                    # Cas d’une liste de dictionnaires
                    valeurs_possibles.extend(elem.values())
                else:
                    valeurs_possibles.append(elem)
        else:
            valeurs_possibles.append(v)
    return valeurs_possibles


# Retourne une liste de widgets (QPushButton) correspondant à un champ spécifique.
def get_widgets_by_champ(parent, champ):
    widgets = []
    for w in parent.findChildren(QWidget):
        if not w.property("iswidgetjson"):
            continue
        if w.property("champ") != champ:
            continue
        if isinstance(w, QPushButton):
            widgets.append(w)
    return widgets

# retrouver un widget en fonction de son "setProperty"
def get_widget_by_champ_valeur(parent, champ, valeur=""):
    """
    Retourne le widget (QPushButton, QComboBox, QLineEdit)
    correspondant à un champ et éventuellement à une valeur.
    """
    for w in parent.findChildren(QWidget):
        # On ne prend que les widgets ajoutés dynamiquement
        if not w.property("iswidgetjson"):
            continue

        # On vérifie d'abord le champ
        if w.property("champ") != champ:
            continue

        # Si c'est un QLineEdit, on le renvoie directement
        if isinstance(w, QLineEdit):
            return w

        if isinstance(w, QDateTimeEdit):
            return w

        # cas des combobox, recherche dans tous les items
        if isinstance(w, QComboBox):
            # Si aucune valeur n'est demandée, on retourne le combo
            if valeur == "":
                return w
            # Sinon, on cherche si la valeur existe dans les éléments du combo
            for i in range(w.count()):
                if str(w.itemText(i)) == str(valeur):
                    return w
            # Si pas trouvé, on continue la recherche
            continue

        # Pour les boutons ou combobox → on compare les valeurs
        widget_val = w.property("valeur")
        if valeur == "" or str(widget_val) == str(valeur):
            return w

    print(f"⚠️ Aucun widget trouvé pour champ='{champ}', valeur='{valeur}'")
    return None

def clear_layout(layout):
    """Supprime tous les widgets d’un QLayout (récursif)."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout():
            clear_layout(item.layout())

def afficheDoc():
    if not os.path.isfile(os.path.join(os.path.dirname(__file__),"jeux d'attributs.pdf")):
        afficheerreur("La documentation est introuvable", "Information")
    else:
        os.popen(os.path.join(os.path.dirname(__file__),"jeux d'attributs.pdf"))

def afficheerreur(text, titre=TITRE):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(titre)
    msg.setWindowIcon(QIcon(PATHICON))
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setTextFormat(Qt.RichText)
    msg.setText(text)
    msg.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.WindowCloseButtonHint)
    msg.exec()

def afficherinformation(text,titre = TITRE):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(titre)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setText(text)
    msg.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.WindowCloseButtonHint)
    msg.exec()

def affichercontraintes(text, titre=TITRE):
    msg = QDialog()
    msg.setWindowIcon(QIcon(PATHICON))
    msg.setWindowTitle(titre)
    # msg.setTextFormat(Qt.RichText)
    # msg.setText(intitule)
    layout = QGridLayout(msg)

    # --- Icône Warning ---
    icon_warning = QLabel()
    icon = QMessageBox().standardIcon(QMessageBox.Warning)
    icon_warning.setPixmap(icon)

    # intitulé
    intitule_widg = QLabel("Les valeurs saisies ne sont pas conformes aux contraintes :")
    intitule_widg.setStyleSheet("color: red;font-weight: bold")

    # text edit
    text_edit = QTextEdit(msg)
    text_edit.setReadOnly(True)
    text = text.replace(" or "," or \n")
    text_edit.setText(text)
    # doc_height = text_edit.document().size().height()  # hauteur du contenu en "points"
    text_edit.setFixedHeight(100)  # +5 pour un petit padding

    layout.addWidget(icon_warning,0,0)
    layout.addWidget(intitule_widg,0,1)
    layout.addWidget(text_edit,1,1)

    msg.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
    msg.exec()




