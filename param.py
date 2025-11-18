import json

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from .constante import *


class ParamDialog(QDialog):

    def __init__(self,parent=None):
        super().__init__(parent)

        loadUi(os.path.dirname(__file__) + "/param.ui", self)
        self.setWindowTitle(TITRE)
        self.setWindowIcon(QIcon(PATHICON))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        # Dictionnaire de paramètres avec valeurs par défaut
        self.dico_param = {
            "nb_btn_ligne": 3,
            "couleur_btn_valider": "#df920d",
            "couleur_btn_selection": "#d0e60c",
            # "couleur_btn_defaut": "None",
            "couleur_btn_commun": "#00b729"
        }

        dico_fichier = self.load_param_json()
        self.dico_param.update(dico_fichier) # garde les valeurs du JSON, mais complète avec les défauts manquants

        self.mColorButton_btn_valider.setColor(QColor(self.dico_param["couleur_btn_valider"]))
        self.mColorButton_btn_sel.setColor(QColor(self.dico_param["couleur_btn_selection"]))
        self.mColorButton_btn_commun.setColor(QColor(self.dico_param["couleur_btn_commun"]))
        list_btn_color = [self.mColorButton_btn_valider, self.mColorButton_btn_sel, self.mColorButton_btn_commun]

        self.spinBoxNbwidget.setRange(0,5)

        self.init_parametre()

        # redefini dorenevant dans main dialogue pour appliquer les modif a la volée
        # self.pushButtonOk.clicked.connect(self.ok)

        self.spinBoxNbwidget.valueChanged.connect(self.spinbox_change)
        for btn_color in list_btn_color:
            btn_color.colorChanged.connect(lambda _, b=btn_color: self.color_change(b))

    def init_parametre(self):
        valeur_spin = self.dico_param.get("nb_btn_ligne",3)
        self.spinBoxNbwidget.setValue(valeur_spin)


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

    # def ok(self):
    #     self.sauve_param_json()
    #
    #     # la fenetre reste ouvert
    #     # self.accept()
