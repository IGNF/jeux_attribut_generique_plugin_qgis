
from qgis.PyQt.QtGui import  QStandardItemModel, QStandardItem, QBrush, QColor
from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtCore import QSortFilterProxyModel


from .fonction import *
from .formulaire import *

class FiltreDialog(QDialog):

    def __init__(self,layer,parent=None):
        super().__init__(parent)

        loadUi(os.path.dirname(__file__) + "/filtre.ui", self)
        self.setWindowTitle(TITRE)
        self.setWindowIcon(QIcon(PATHICON))
        self.setWindowFlags(WindowStaysOnTopHint | WindowCloseButtonHint)

        self.layer = layer


        self.lineEdit_recherche.textChanged.connect(self.filtre_tree)

        self.ini_treeview()
        self.radioButton_alldecoche.toggled.connect(self.all_decocher)
        self.radioButton_allcoche.toggled.connect(self.all_cocher)
        self.pushButtonOk.clicked.connect(self.ok)

    def all_decocher(self):
        for row in range(self.model.rowCount()):
            item_parent = self.model.item(row, 0)
            item_parent.setCheckState(Unchecked)

            for i in range(item_parent.rowCount()):
                child = item_parent.child(i, 0)
                child.setCheckState(Unchecked)


    def all_cocher(self):
        for row in range(self.model.rowCount()):
            item_parent = self.model.item(row, 0)
            item_parent.setCheckState(Checked)
            for i in range(item_parent.rowCount()):
                child = item_parent.child(i, 0)
                child.setCheckState(Checked)


    def ini_treeview(self):
        dico_champs_val = {}
        dico_types = {}

        filtre_layer = loadjson(self.layer.name())

        for type_champ, liste_champs in get_champs(self.layer).items():
            for champ in liste_champs:
                dico_types[champ] = type_champ
                valeurs = get_valeur(self.layer, champ)
                dico_champs_val[champ] = valeurs

        self.model = QStandardItemModel()
        # slot pour gerer le fait de decocher les item enfants en fct du parent
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.setHorizontalHeaderLabels(["Champ / valeur"])

        brushfond1 = QBrush()
        brushfond1.setStyle(SolidPattern)
        brushfond1.setColor(QColor(230, 230, 230))

        brushfond2 = QBrush()
        brushfond2.setStyle(SolidPattern)
        brushfond2.setColor(QColor(200, 200, 200))

        brushtext1= QBrush()
        brushtext1.setStyle(SolidPattern)
        brushtext1.setColor(QColor(0, 107, 24))

        brushtext2 = QBrush()
        brushtext2.setStyle(SolidPattern)
        brushtext2.setColor(QColor(0, 107, 24))

        brush_noeditable = QBrush()
        brush_noeditable.setStyle(SolidPattern)
        brush_noeditable.setColor(QColor(255, 40, 40))

        self.label_noeditable.setStyleSheet("color: rgb(255,40,40)")

        for champ, valeurs in dico_champs_val.items():
            # test si champ est editable ou pas
            read_only = isreadonly(self.layer,champ)

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
                champ_item.setCheckState(Checked)

            if dico_types[champ] == "ValueMap":
                for val in valeurs:
                    val_item = QStandardItem(str(val))
                    val_item.setEditable(False)
                    val_item.setBackground(brushfond2)
                    if read_only:
                        val_item.setForeground(brush_noeditable)
                    else:
                        val_item.setForeground(brushtext2)
                    val_item.setCheckable(True)
                    # Si la valeur est cochée dans le JSON → cocher
                    if champ in filtre_layer and val in filtre_layer[champ]:
                        val_item.setCheckState(Checked)
                    champ_item.appendRow(val_item)
            self.model.appendRow(champ_item)

        # PROXY (pour la recherche)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(0)  # on filtre sur la première colonne

        # Important pour treeView avec hiérarchie
        self.proxy_model.setRecursiveFilteringEnabled(True)

        # Lier proxy à la vue
        self.treeView.setModel(self.proxy_model)

    def filtre_tree(self, texte):
        self.proxy_model.setFilterRegularExpression(texte)
        text = self.lineEdit_recherche.text()
        if text == "":
            self.treeView.collapseAll()
        else:
            self.treeView.expandAll()

    def on_item_changed(self, item):
        # model = self.treeView.model()
        self.model.blockSignals(True)

        state = item.checkState()

        # on coche un parent
        if item.hasChildren():
            # Si le parent est décoché, décocher tous les enfants
            if state == Unchecked:
                for i in range(item.rowCount()):
                    child = item.child(i)
                    child.setCheckState(Unchecked)

            # Si le parent est coché -> cocher tous les enfants (optionnel)
            elif state == Checked:
                for i in range(item.rowCount()):
                    child = item.child(i)
                    child.setCheckState(Checked)

        # on coche un enfant -->  le parent se coche
        else:
            parent = item.parent()
            if parent:
                # Si au moins un enfant est coché -> cocher le parent
                any_checked = any(
                    parent.child(i).checkState() == Checked
                    for i in range(parent.rowCount())
                )
                parent.setCheckState(Checked if any_checked else Unchecked)

        self.model.blockSignals(False)

        self.proxy_model.invalidate()  # recalcul du filtre
        self.treeView.viewport().update()


    def getcheckitem(self):
        # model = self.treeView.model()
        model = self.model
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
                if val_item.checkState() == Checked:
                    valeurs.append(val_item.text())

            # On ajoute le champ seulement si :
            # - au moins une valeur est cochée
            # - ou s’il n’a pas de valeurs enfants (facultatif selon ton besoin)
            if valeurs:
                dico_checked[champ_name] = valeurs
            elif champ_item.rowCount() == 0 and champ_item.checkState() == Checked:
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

    def nb_parent_coche(self):
        count = 0
        rows = self.model.rowCount()
        for row in range(rows):
            item = self.model.item(row)
            if item.checkState() == Checked:
                count += 1
        return count

    def ok(self):
        nb_champ_coche = self.nb_parent_coche()
        if nb_champ_coche >NB_CHAMP_MAX:
            text = f"Vous voulez ajouter trop de valeurs , la fenêtre va dépasser de l'écran {CLIN_OEIL}<br>"
            text += f"La limite est de <span style='color: red'><b>{NB_CHAMP_MAX} </b></span>valeurs<br>"
            text += f"Vous voulez en afficher : <span style='color: red'><b>{nb_champ_coche}</b></span>"
            afficheerreur(text,"Trop de champs ajoutés")
            return

        # sauvegarde de la config
        self.sauvjson()

        self.accept()

