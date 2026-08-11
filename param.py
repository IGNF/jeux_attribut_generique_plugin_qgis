import json

from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtGui import QIcon, QColor, QRegularExpressionValidator
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtCore import QRegularExpression

from .constante import *


class ParamDialog(QDialog):

    def __init__(self,parent=None):
        super().__init__(parent)

        loadUi(os.path.dirname(__file__) + "/param.ui", self)
        self.setWindowTitle(TITRE)
        self.setWindowIcon(QIcon(PATHICON))
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Dictionnaire de paramètres avec valeurs par défaut
        self.dico_param = {
            "nb_btn_ligne": 3,
            "couleur_btn_valider": "#df920d",
            "couleur_btn_selection": "#d0e60c",
            # "couleur_btn_defaut": "None",
            "couleur_btn_commun": "#00b729",
            "taille_font": TAILLE_FONT_DEFAUT
        }

        dico_fichier = self.load_param_json()
        self.dico_param.update(dico_fichier) # garde les valeurs du JSON, mais complète avec les défauts manquants

        self.mColorButton_btn_valider.setColor(QColor(self.dico_param["couleur_btn_valider"]))
        self.mColorButton_btn_sel.setColor(QColor(self.dico_param["couleur_btn_selection"]))
        self.mColorButton_btn_commun.setColor(QColor(self.dico_param["couleur_btn_commun"]))
        list_btn_color = [self.mColorButton_btn_valider, self.mColorButton_btn_sel, self.mColorButton_btn_commun]

        self.spinBoxNbwidget.setRange(0,10)

        # regex pour la contrainte de saisi de la taille des btn
        regex = QRegularExpression(r"^(?:[6-9]|1\d|2\d|30)$")
        validator = QRegularExpressionValidator(regex, self.lineEdit_taille_font)
        self.lineEdit_taille_font.setValidator(validator)
        # masque le warning
        self.label_warning.hide()

        self.init_parametre()

        # redéfini dorénavant dans main dialogue pour appliquer les modifs à la volée
        # self.pushButtonOk.clicked.connect(self.ok)

        # événement spinBoxNbwidget change
        self.spinBoxNbwidget.valueChanged.connect(self.spinbox_change)
        # événement color change
        for btn_color in list_btn_color:
            btn_color.colorChanged.connect(lambda _, b=btn_color: self.color_change(b))

        # événement edit_taille_btn change
        self.lineEdit_taille_font.textChanged.connect(self.taille_btn_change)

    def init_parametre(self):
        valeur_spin = self.dico_param.get("nb_btn_ligne",3)
        self.spinBoxNbwidget.setValue(valeur_spin)
        self.lineEdit_taille_font.setText(str(self.dico_param.get("taille_btn", TAILLE_FONT_DEFAUT)))


    def color_change(self,btn):
        color = btn.color().name()

        # dans le dico les clé sont un str et nom l'instance des widgets
        # donc on associe chaque bouton à la bonne clé du dico
        mapping = {
            self.mColorButton_btn_valider: "couleur_btn_valider",
            self.mColorButton_btn_sel: "couleur_btn_selection",
            self.mColorButton_btn_commun: "couleur_btn_commun",
        }
        cle = mapping.get(btn)
        if cle:
            self.dico_param[cle] = color
        # color = self.mColorButton_btn_valider.color().name()
        # self.dico_param["couleur_btn_valider"] = color

    def spinbox_change(self, value):
        # self.nb_widg_par_ligne = value
        self.dico_param["nb_btn_ligne"] = value

    def taille_btn_change(self):
        taille = self.lineEdit_taille_font.text()
        if taille == "":
            return  # on ne fait rien tant que vide
        if self.lineEdit_taille_font.hasAcceptableInput():
            self.label_warning.hide()
            self.lineEdit_taille_font.setStyleSheet("")
            self.dico_param["taille_btn"] = int(self.lineEdit_taille_font.text())
        else:
            self.label_warning.show()
            self.lineEdit_taille_font.setStyleSheet("background-color: #ffa8a8")


    def load_param_json(self):
        """Charge le fichier JSON des paramètres s’il existe."""
        try:
            with open(PATHJSONPARAM, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            with open(PATHJSONPARAM, "w", encoding="utf-8") as f:
                json.dump(self.dico_param, f, ensure_ascii=False, indent=2)
            return self.dico_param.copy()
        except Exception as e:
            return {}

    def sauve_param_json(self):
        """Sauvegarde les paramètres dans un fichier JSON."""
        try:
            os.makedirs(os.path.dirname(PATHJSONPARAM), exist_ok=True)
            with open(PATHJSONPARAM, "w", encoding="utf-8") as f:
                json.dump(self.dico_param, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde JSON : {e}")
