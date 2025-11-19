import os

from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

import json

from .constante import *
from .fonction import *

class FiltreDialog(QDialog):

    def __init__(self,layer,parent=None):
        super().__init__(parent)

        loadUi(os.path.dirname(__file__) + "/filtre.ui", self)
        self.setWindowTitle(TITRE)
        self.setWindowIcon(QIcon(PATHICON))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        self.layer = layer


        self.ini_treeview()
        self.checkBox_alldecocher.stateChanged.connect(self.checkbox_changed)
        self.pushButtonOk.clicked.connect(self.ok)

    def checkbox_changed(self,etat):
        if etat == Qt.Checked:
            print("on decoche")
            model = self.treeView.model()
            # enfants
            for row in range(model.rowCount()):
                item_parent = model.item(row, 0)
                # if item_parent is not None:
                # item_parent.setCheckState(Qt.Unchecked)
                for i in range(item_parent.rowCount()):
                    child = item_parent.child(i, 0)
                    child.setCheckState(Qt.Unchecked)

            # parent
            for row in range(model.rowCount()):
                item_parent = model.item(row, 0)
                item_parent.setCheckState(Qt.Unchecked)



    def ini_treeview(self):
        dico_champs_val = {}
        dico_types = {}

        filtre_layer = loadjson(self.layer.name())

        for type_champ, liste_champs in get_champs(self.layer).items():
            for champ in liste_champs:
                dico_types[champ] = type_champ
                valeurs = get_valeur(self.layer, champ)
                dico_champs_val[champ] = valeurs

        model = QStandardItemModel()
        # slot pour gerer le fait de decocher les item enfants en fct du parent
        model.itemChanged.connect(self.on_item_changed)
        model.setHorizontalHeaderLabels(["Champ / valeur"])

        brushfond1 = QBrush()
        brushfond1.setStyle(Qt.SolidPattern)
        brushfond1.setColor(QColor(230, 230, 230))

        brushfond2 = QBrush()
        brushfond2.setStyle(Qt.SolidPattern)
        brushfond2.setColor(QColor(200, 200, 200))

        brushtext1= QBrush()
        brushtext1.setStyle(Qt.SolidPattern)
        brushtext1.setColor(QColor(0, 107, 24))

        brushtext2 = QBrush()
        brushtext2.setStyle(Qt.SolidPattern)
        brushtext2.setColor(QColor(0, 107, 24))

        brush_noeditable = QBrush()
        brush_noeditable.setStyle(Qt.SolidPattern)
        brush_noeditable.setColor(QColor(255, 40, 40))

        self.label_noeditable.setStyleSheet("color: rgb(255,40,40)")

        for champ, valeurs in dico_champs_val.items():
            # test si champ est editable ou pas
            # si oui on ajoute dans le treeview en rouge
            index = self.layer.fields().indexOf(champ)
            form_config = self.layer.editFormConfig()
            read_only = form_config.readOnly(index)

            champ_item = QStandardItem(champ)
            champ_item.setEditable(False)
            champ_item.setBackground(brushfond1)
            champ_item.setForeground(brushtext1)

            if read_only:
                champ_item.setForeground(brush_noeditable)
            else:
                champ_item.setForeground(brushtext1)

            champ_item.setCheckable(True)

            # Si le champ est présent dans le JSON → cocher le champ
            if champ in filtre_layer:
                champ_item.setCheckState(Qt.Checked)

            if dico_types[champ] == "ValueMap":
                for val in valeurs:
                    val_item = QStandardItem(str(val))
                    val_item.setEditable(False)
                    val_item.setForeground(brushtext2)
                    val_item.setBackground(brushfond2)
                    val_item.setCheckable(True)
                    # Si la valeur est cochée dans le JSON → cocher
                    if champ in filtre_layer and val in filtre_layer[champ]:
                        val_item.setCheckState(Qt.Checked)
                    champ_item.appendRow(val_item)
            model.appendRow(champ_item)

        self.treeView.setModel(model)
        # self.treeView.expandAll()

    def on_item_changed(self, item):
        model = self.treeView.model()
        model.blockSignals(True)

        state = item.checkState()

        if item.hasChildren():
            # Si le parent est décoché, décocher tous les enfants
            if state == Qt.Unchecked:
                for i in range(item.rowCount()):
                    child = item.child(i)
                    child.setCheckState(Qt.Unchecked)

        # else:
        #     # Si c’est un enfant, cocher le parent si au moins un enfant est coché
        #     parent = item.parent()
        #     if parent:
        #         for i in range(parent.rowCount()):
        #             if parent.child(i).checkState() == Qt.Checked:
        #                 parent.setCheckState(Qt.Checked)
        #                 break

        model.blockSignals(False)

        # else:
        #     # Si c’est un enfant (valeur)
        #     parent = item.parent()
        #     if parent is not None:
        #         # Vérifie si au moins une valeur est cochée
        #         any_checked = any(parent.child(i).checkState() == Qt.Checked for i in range(parent.rowCount()))
        #
        #         # 🔒 Bloquer pendant la mise à jour du parent
        #         model.blockSignals(True)
        #         parent.setCheckState(Qt.Checked if any_checked else Qt.Unchecked)
        #         model.blockSignals(False)


    def getcheckitem(self):
        model = self.treeView.model()
        dico_checked = {}

        # Parcourir tous les champs (nœuds racine)
        for i in range(model.rowCount()):
            champ_item = model.item(i)
            champ_name = champ_item.text()
            valeurs = []

            # Si le champ est coché, on l'ajoute (même sans valeurs)
            # sauf si champs est de type Valuemap et qu'aucunes valeur est coché

            # Parcourir toutes les valeurs enfants
            for j in range(champ_item.rowCount()):
                val_item = champ_item.child(j)
                if val_item.checkState() == Qt.Checked:
                    valeurs.append(val_item.text())

            # On ajoute le champ seulement si :
            # - au moins une valeur est cochée
            # - ou s’il n’a pas de valeurs enfants (facultatif selon ton besoin)
            if valeurs:
                dico_checked[champ_name] = valeurs
            elif champ_item.rowCount() == 0 and champ_item.checkState() == Qt.Checked:
                # cas spécial : champ sans enfants
                dico_checked[champ_name] = []
        return dico_checked


    def sauvjson(self):
        layer = self.layer.name()

        # Charger le fichier existant ou créer un dictionnaire vide pour ajouter
        # sinon on perd les valeurs des autres layers
        try:
            with open(PATHJSON, "r", encoding="utf-8") as f:
                filtre_par_couche = json.load(f)
        except FileNotFoundError:
            filtre_par_couche = {}

        filtre_par_couche[layer] = self.getcheckitem()
        # Sauvegarde du json
        try:
            with open(PATHJSON, "w", encoding="utf-8") as f:
                json.dump(filtre_par_couche, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde JSON : {e}")

    def ok(self):
        # tester si on a bien cliqué dans une valeur si on clic dans un champ
        # si valeur vide → on retire le champ

        # sauvegarde de la config
        self.sauvjson()

        self.accept()

