

from PyQt5.QtCore import QObject, QEvent, QSize, QDate, QTime
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QVBoxLayout,QSizePolicy, QFrame, QInputDialog
from PyQt5.uic import loadUi
from qgis._core import QgsMapLayer
from qgis.core import  QgsExpression,QgsExpressionContext, QgsExpressionContextUtils ,Qgis


from .filtre import FiltreDialog
from .param import ParamDialog
from .cheminpluscourt import *
from .fonction import *

class FiltreClicDroit(QObject):
    def __init__(self, class_parent):
        super().__init__()
        self.class_parent = class_parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if isinstance(obj, QPushButton):
                self.class_parent.clic_droit(obj)
                return True
                # QMessageBox.warning(None, "fd","sdf")
            # Cas d’un clic droit sur un item du QComboBox
            # le clic se fait sur le viewport
            elif isinstance(obj, QWidget):  # obj = viewport du QListView
                self.class_parent.clic_droit_combobox(obj,event)
        return False

class MainDialog(QDialog):

    def __init__(self ,iface,layer,plugin,parent=None):
        super().__init__(parent)

        self.get_contraintes = {}
        self.dlgFiltre = None
        self.dico_filtre = None

        # avant modif
        self.dico_val_linedit = {}

        self.plugin = plugin
        self.iface = iface
        self.layer = layer
        self.is_affiche_sens_num = False
        self.cheminpluscourt = None

        # TODO à supprimer pour déploiement (ça ouvre la console)
        # console = self.iface.mainWindow().findChild(QObject, "PythonConsole")
        # if not console or not console.isVisible():
        #     self.iface.actionShowPythonDialog().trigger()


        self.widget_clique = {}
        self.combo_widgets = {}

        self.dlgParam = ParamDialog()
        self.dico_param = self.dlgParam.load_param_json()
        self.nb_widget_par_ligne = self.dico_param.get("nb_btn_ligne", 3)
        self.color_btn_valider = self.dico_param.get("couleur_btn_valider", "#e648e7")
        self.color_btn_sel = self.dico_param.get("couleur_btn_selection", "#2ab51a")
        self.color_btn_commun = self.dico_param.get("couleur_btn_commun", "#ff8080")
        self.taille_btn = self.dico_param.get("taille_btn", 30)

        self.setWindowTitle(f"{TITRE} {VERSION}")
        self.setWindowIcon(QIcon(PATHICON))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        self.filtre_clic_droit = FiltreClicDroit(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)  # (gauche, haut, droite, bas)

        layout_widget_permanent = QHBoxLayout()

        # ajout du bouton filtre
        self.btn_filtre = QPushButton()
        self.btn_filtre.setIcon(QIcon(PATHICON_FILTRE))
        self.btn_filtre.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_filtre.setIconSize(QSize(self.btn_filtre.width() - 8, self.btn_filtre.height() - 8))
        self.btn_filtre.setToolTip("Ajouter/supprimer des boutons")
        layout_widget_permanent.addWidget(self.btn_filtre)

        # bouton parametre
        self.btn_param = QPushButton()
        self.btn_param.setIcon(QIcon(PATHICON_PARAM))
        self.btn_param.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_param.setIconSize(QSize(self.btn_param.width() - 8, self.btn_param.height() - 8))
        self.btn_param.setToolTip("Modifier les couleurs et le nombre de boutons par ligne")
        layout_widget_permanent.addWidget(self.btn_param)

        # bouton sens de numérisation
        self.btn_sens_num = QPushButton()
        self.btn_sens_num.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_sens_num.setIconSize(QSize(self.btn_sens_num.width()-2,self.btn_sens_num.height()-2))
        self.btn_sens_num.setIcon(QIcon(PATHICON_SENS_NUM))
        self.btn_sens_num.setToolTip("Afficher / Masquer le sens de numérisation")
        layout_widget_permanent.addWidget(self.btn_sens_num)

        # bouton chemin plus court
        self.btn_che_court = QPushButton()
        self.btn_che_court.setIcon(QIcon(PATHICON_CHE_COURT))
        self.btn_che_court.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_che_court.setIconSize(QSize(self.btn_che_court.width() - 8, self.btn_che_court.height() - 8))
        self.btn_che_court.setToolTip("Chemin le plus court")
        layout_widget_permanent.addWidget(self.btn_che_court)

        # ajout du bouton apropos
        self.btn_apropos = QPushButton("?")
        self.btn_apropos.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_apropos.setIconSize(QSize(self.btn_apropos.width() - 8, self.btn_apropos.height() - 8))
        self.btn_apropos.setToolTip("A propos de")
        layout_widget_permanent.addWidget(self.btn_apropos)

        # Ajout du bouton "valider"
        layout_widget_permanent.addStretch()
        self.btn_valider = QPushButton("Valider les modifications")
        self.btn_valider.setFixedSize(150, TAILLE_BTN_DEFAUT)
        self.btn_valider.setIconSize(QSize(self.btn_valider.width() - 8, self.btn_valider.height() - 8))
        self.btn_valider.setStyleSheet(f"font-weight: bold;background-color: {self.color_btn_valider}")
        layout_widget_permanent.addWidget(self.btn_valider)

        # bouton importer/exporter
        self.btn_importer = QPushButton()
        self.btn_importer.setIcon(QIcon(PATHICON_IMPORT))
        self.btn_importer.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_importer.setIconSize(QSize(self.btn_importer.width() - 8, self.btn_importer.height() - 8))
        self.btn_importer.setToolTip("Importer la configuration")
        layout_widget_permanent.addWidget(self.btn_importer)
        self.btn_exporter = QPushButton()
        self.btn_exporter.setIcon(QIcon(PATHICON_EXPORT))
        self.btn_exporter.setFixedSize(TAILLE_BTN_DEFAUT, TAILLE_BTN_DEFAUT)
        self.btn_exporter.setIconSize(QSize(self.btn_exporter.width() - 8, self.btn_exporter.height() - 8))
        self.btn_exporter.setToolTip("Exporter la configuration")
        layout_widget_permanent.addWidget(self.btn_exporter)
        layout_widget_permanent.addStretch()

        # ajout du label du nombre de selection
        self.label_nbsel = QLabel()
        layout_widget_permanent.addWidget(self.label_nbsel)

        self.formlayout = QFormLayout()
        self.formlayout.setSpacing(1)

        # ajout des 2 layouts (permanent et layout des btn) separés par une ligne
        main_layout.addLayout(self.formlayout)
        # --- AJOUT DE LA LIGNE HORIZONTALE ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("""color: #808080;background-color: #808080;""")
        main_layout.addWidget(line)
        # --------------------------------------
        layout_widget_permanent.setSpacing(0)
        main_layout.addLayout(layout_widget_permanent)

        # Connexion des signaux
        self.btn_valider.clicked.connect(self.valide_modif)
        self.btn_filtre.clicked.connect(self.gestionfiltre)
        self.btn_apropos.clicked.connect(self.apropos)
        self.btn_param.clicked.connect(self.show_param)
        self.btn_importer.clicked.connect(lambda:importer_json(self)) # self -> pour lier le qmessage au dlg pour passer devant
        self.btn_exporter.clicked.connect(lambda:exporter_json(self))
        self.btn_sens_num.clicked.connect(self.affiche_sens_num)

        # le slot de "btn_che_court" est declaré dans jeux_attributs.py
        # btn_che_court.clicked.connect(self.che_plus_court)

    def affiche_sens_num(self):
        if self.is_affiche_sens_num:
            # chargement de la symbologie ET des etiquettes
            self.layer.loadNamedStyle(os.path.join(PATH_REP ,"sauvegarde_style_initial.qml"),categories=QgsMapLayer.StyleCategory.Symbology| QgsMapLayer.Labeling)
            self.is_affiche_sens_num = False
        else:
            # sauvegarde de la symbologie ET des etiquettes
            self.layer.saveNamedStyle(os.path.join(PATH_REP ,"sauvegarde_style_initial.qml"),categories=QgsMapLayer.StyleCategory.Symbology| QgsMapLayer.Labeling)
            self.layer.loadNamedStyle(os.path.join(PATH_REP ,"style_sens_numerisation.qml"),categories=QgsMapLayer.StyleCategory.Symbology| QgsMapLayer.Labeling)
            self.is_affiche_sens_num = True
        self.layer.triggerRepaint()

    def che_plus_court(self):
        if self.layer.selectedFeatureCount() != 2:
            QMessageBox.warning(self,TITRE,"Veuillez sélectionner exactement 2 tronçons")
            return
        # sauvegarde du layer pour le restituer apres le calcul du chemin le plus court
        layer_avant = self.layer
        # instanciation de la class dhemin le plus court
        self.cheminpluscourt = cheminpluscourt(self.iface, self.layer)
        self.cheminpluscourt.cheminpluscourt()

        self.set_active_layer(layer_avant.name())
        # IMPORTANT : laisser le temps du chemin le plus court de finir la selection
        # avant d’appeler actualiserSelection()
        QTimer.singleShot(0, self.plugin.actualiserSelection)

    def set_active_layer(self,layer_name):
        project = QgsProject.instance()
        couche = project.mapLayersByName(layer_name)
        self.iface.setActiveLayer(couche[0])
        self.layer = self.iface.activeLayer()


    def deplace_btn_to_json(self,champ,valeur):
        # charger TOUT le json (donc ne pas passer par la fonction loadjson qui charge que le layer donné)
        with open(PATHJSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        valeur_par_champ = data[self.layer.name()][champ]
        pos, ok = QInputDialog.getInt(
            self,
            "Modifier la position",
            f"Position de <span style='color: red'><b>'{champ}'</b></span>"
            f"{SEPARATION_TOOLTIP}<span style='color: red'><b>'{valeur}'</b></span>",
            value=1,
            min=1,
            max=len(valeur_par_champ)+1,
            step=1
        )
        valeur_par_champ.remove(valeur)
        valeur_par_champ.insert(pos - 1, valeur)

        # Sauvegarde du JSON complet (structure conservée)
        try:
            with open(PATHJSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f" Erreur sauvegarde JSON : {e}")

    def clic_droit(self,obj):
        champ = obj.property("champ")
        valeur = obj.property("valeur")
        self.deplace_btn_to_json(champ,valeur)


    def clic_droit_combobox(self,obj,event):
        view = obj.parent()  # -> QListView
        if hasattr(view, "indexAt"): # s'assurer que view possede bien la methode indexAt() ->QListView
            # 🔹 Remonter la hiérarchie jusqu’à trouver le QComboBox
            combo = view
            while combo is not None and not isinstance(combo, QComboBox):
                combo = combo.parent()

            index = view.indexAt(event.pos())
            if index.isValid():
                champ = combo.property("champ")
                valeur = index.data(Qt.DisplayRole)
                self.deplace_btn_to_json(champ, valeur)
                # on actualise l'interface
                self.plugin.dico_filtre =  loadjson(self.layer.name())
                self.plugin.add_all_widget()
                QTimer.singleShot(0, self.plugin.actualiserSelection)
                return True

        return False

    def add_widget(self,champ,valeurs,typewidget):
        # formatage du nom des champs (suppr des _)
        text_label = champ.replace("_", " ").replace("l ", "l'").replace("d ", "d'").capitalize() + " :  "
        style = "<span style= 'color: #b63d3d; font-weight: bold'>"
        champ_format = QLabel(f"{style}{text_label}</span>")

        hlayout = QHBoxLayout()
        hlayout.setSpacing(1)

        # test si le champ est editable ou pas
        index = self.layer.fields().indexOf(champ)
        form_config = self.layer.editFormConfig()
        read_only = form_config.readOnly(index)

        if typewidget == "DateTime":
            widgdatetime = QDateTimeEdit()
            widgdatetime.setReadOnly(read_only)
            widgdatetime.setEnabled(not read_only)
            widgdatetime.setFixedWidth(180)
            widgdatetime.setProperty("champ", champ)
            widgdatetime.setProperty("valeur", "")
            widgdatetime.setProperty("iswidgetjson", typewidget)
            hlayout.addWidget(widgdatetime)

        if typewidget == "TextEdit":
            lineedit = QLineEdit()
            # on désactive le menu contextuel d'un clic droit par défaut sur un lineedit
            lineedit.setContextMenuPolicy(Qt.NoContextMenu)
            lineedit.setReadOnly(read_only)
            lineedit.setEnabled(not read_only)
            lineedit.setFixedWidth(180)
            lineedit.setFixedHeight(self.taille_btn)
            lineedit.setProperty("champ", champ)
            # valeur = "" pour gérer l'aspect du widget
            lineedit.setProperty("valeur", "")
            lineedit.setProperty("iswidgetjson", True)
            hlayout.addWidget(lineedit)
            # lineedit.textChanged.connect(lambda v, c=champ: self.textedit_sel(c, v))
            # textEdited == uniquement si modif pad UTILISATEUR
            lineedit.textEdited.connect(lambda v, c=champ: self.textedit_sel(c, v))
            lineedit.editingFinished.connect(lambda c=champ,widg=lineedit:self.on_perte_focus(c, widg.text()))

        else:
            for val in valeurs[:self.nb_widget_par_ligne]:
                btn = QPushButton(str(val))
                btn.setEnabled(not read_only)
                btn.setFixedHeight(self.taille_btn)
                btn.setProperty("champ",champ)
                btn.setProperty("valeur", val)
                btn.setProperty("iswidgetjson", True)
                btn.setToolTip(str(val))
                btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
                hlayout.addWidget(btn)

                # gestion clic droit
                btn.installEventFilter(self.filtre_clic_droit)

                btn.clicked.connect(lambda _, c=champ, v=val: self.bouton_sel(c, v))

            if len(valeurs) == self.nb_widget_par_ligne + 1:
                val = valeurs[-1]
                btn = QPushButton(str(val))
                btn.setFixedHeight(self.taille_btn)
                btn.setProperty("champ",champ)
                btn.setProperty("valeur", val)
                btn.setProperty("iswidgetjson", True)
                btn.setToolTip(str(val))
                btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
                hlayout.addWidget(btn)
                btn.clicked.connect(lambda _, c=champ ,v=val: self.bouton_sel(c, v))

            elif len(valeurs) > self.nb_widget_par_ligne + 1:
                combo = QComboBox()
                combo.setEnabled(not read_only)

                combo.addItems([str(val) for val in valeurs[self.nb_widget_par_ligne:]])

                combo.setFixedHeight(self.taille_btn)
                combo.setProperty("champ", champ)
                combo.setProperty("valeur", combo.currentText())
                combo.setProperty("iswidgetjson", True)
                # on stock le combo
                self.combo_widgets[champ] = combo
                combo.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
                hlayout.addWidget(combo)

                # gestion clic droit
                # eventfilter pas sur le combo directement mais sur le view (contenu)
                combo.view().viewport().installEventFilter(self.filtre_clic_droit)
                combo.activated.connect(lambda v, c=champ: self.combobox_sel(c, combo.itemText(v)))

        self.formlayout.addRow(champ_format, hlayout)

    def add_widget_from_filtre(self):
        """Construit les widgets selon les filtres"""
        clear_layout(self.formlayout)
        dico_champs = get_champs(self.layer)

        for type_champ, champs in dico_champs.items():
            for champ in champs:
                if champ not in self.dico_filtre:
                    continue
                valeurs = self.dico_filtre[champ]
                self.add_widget(champ, valeurs,type_champ)

        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    # initialise les btn en fonction des attributs communs, et si present dans le json (-->couleur)
    def get_attributs_communs(self):
        if self.layer.selectedFeatureCount() ==0:
            return
        config = loadjson(self.layer.name())
        liste_valeur_sel = []

        for champ in config.keys():
            liste_valeur_sel.clear()
            for sel in self.layer.selectedFeatures():
                idchamps = self.layer.fields().indexFromName(champ)
                attr = sel.attributes()
                val = attr[idchamps]
                liste_valeur_sel.append(val)
            if not liste_valeur_sel:
                continue

            # Si toutes les valeurs sont identiques
            if len(set(liste_valeur_sel)) == 1:
                val_unique = liste_valeur_sel[0]
                widget = get_widget_by_champ_valeur(self, champ,val_unique)
                # on initialise les items des combos a "blanc".
                # print(f"val unique : champ - valeur = {champ}-{val_unique}")
                # si c'est un bouton
                if isinstance(widget, QPushButton):
                    self.set_all_item_color(champ,None)
                    self.set_color_btn(champ,val_unique,self.color_btn_commun)
                # si c'est un combobox
                if isinstance(widget, QComboBox):
                    # print("la valeur est dans le combo")
                    # Vérifie si la valeur existe déjà dans le combo
                    index = widget.findText(val_unique)
                    if index != -1:
                        # Supprime l'entrée existante
                        widget.removeItem(index)
                        # Insère la valeur au début (position 0)
                        widget.insertItem(0, val_unique)
                        # Sélectionne cette valeur
                        widget.setCurrentIndex(0)
                    self.set_color_itemcombo(champ,val_unique,self.color_btn_commun)

                # Si c’est un champ texte
                if isinstance(widget, QLineEdit):
                    # sauvegarde des valeurs des linedit pour gérer le rétablissement de la valeur si pas bonne
                    self.dico_val_linedit[champ] = val_unique
                    widget.setText(str(val_unique))
                    widget.setStyleSheet(f"background-color: {self.color_btn_commun}")

                if isinstance(widget, QDateTimeEdit):
                    val_sans_ms = val_unique.split(".")[0]
                    date_format = "yyyy-MM-dd HH:mm:ss"
                    qdt = QDateTime.fromString(val_sans_ms, date_format)
                    widget.setDateTime(qdt)

            # Sinon (plusieurs valeurs différentes)
            else:
                widget = get_widget_by_champ_valeur(self, champ)
                if isinstance(widget, QLineEdit):
                    widget.setText("***")  # afficher *** pour ambiguïté
                    # widget.setStyleSheet("font-weight: bold;background-color: None")
                    widget.setStyleSheet("background-color: None")
                    self.dico_val_linedit[champ] = "***"

                elif isinstance(widget, QDateTimeEdit):
                    widget.setDateTime(QDateTime(QDate(1900, 1, 1), QTime(0, 0, 0)))
                    widget.setStyleSheet("background-color: None")

                elif isinstance(widget, QComboBox):
                    self.set_color_itemcombo(champ,None,None)
                    widget.setStyleSheet("background-color: None")

                elif isinstance(widget, QPushButton):
                    widget.setStyleSheet("background-color: None")

    # changer la couleur du bouton sauf celui qui est en self.color_btn_commun
    def set_color_btn(self,champ,val,color = None):
        widget = get_widget_by_champ_valeur(self, champ, val)
        # initialise tous les widgets a color None sauf celui qui a la color à self.color_btn_commun
        for w in self.findChildren(QWidget):
            style = w.styleSheet()
            if w.property("champ") == champ:
                if style != f"background-color: {self.color_btn_commun}":
                    # Remet la couleur par défaut
                    w.setStyleSheet("background-color: None")

        # on met le widget concerné a color donné en parametre s'il est pas en color : self.color_btn_commun
        if widget.styleSheet() != f"background-color: {self.color_btn_commun}":
            widget.setStyleSheet(f"background-color: {color}")

    def set_all_btn_color(self,champ,color):
        widgets = get_widgets_by_champ(self,champ)
        for wid in widgets:
            # print(wid.property("valeur"))
            style = wid.styleSheet()
            if style == f"background-color: {self.color_btn_commun}":
                continue
            wid.setStyleSheet(f"background-color: {color}")

    # TODO : a faire : ne pas changer si l'item est deja a self.color_btn_commun
    def set_all_item_color(self,champ,color):
        if color is None:
            color = "White"
        combo = self.combo_widgets.get(champ)
        if combo:
            model = combo.model()
            for i in range(model.rowCount()):
                index = model.index(i, 0)
                model.setData(index, QColor(color), Qt.BackgroundRole)

    # on modifie la couleur SAUF si l'item a la couleur : self.color_btn_commun'
    def set_color_itemcombo(self,champ,val=None,color = None):
        # print(f"set_color_itemcombo : {champ} : {val}")
        # on initilaise tous les item a color blanc
        combo = get_widget_by_champ_valeur(self, champ,val)
        if combo is None:
            return
        model = combo.model()

        for i in range(model.rowCount()):
            index = model.index(i, 0)
            texte = model.data(index)
            current_color = model.data(index, Qt.BackgroundRole)
            if current_color == QColor(self.color_btn_commun):
                continue
            model.setData(index, QColor("White"), Qt.BackgroundRole)
            # if texte == val and style != f"background-color: {self.color_btn_commun}":
            if texte == val :
                model.setData(index, QColor(color), Qt.BackgroundRole)
            else:
                model.setData(index, QColor("White"), Qt.BackgroundRole)

        # On colore aussi le fond visible du combo si la valeur est sélectionnée
        # ce qui est toujours le cas apres get_attributs_communs
        # on ne garde la couleur commune que si l'item a la couleur commune.
        if combo.currentText() == val:
                combo.setStyleSheet(f"QComboBox {{ background-color: {color}; }}")
        else:
            combo.setStyleSheet("QComboBox { background-color: white; }")


    # slot textedit
    def textedit_sel(self, champ, val):
        widget = get_widget_by_champ_valeur(self,champ,val)
        widget.setStyleSheet(f"background-color: {self.color_btn_sel}")

        index_champs = self.layer.fields().indexOf(champ)
        if val != "***":
            self.widget_clique[index_champs] = val

    # slot : perte du focus pour gerer les contraintes de saisie sur les lineedit
    def on_perte_focus(self,champ,val):
        widget = get_widget_by_champ_valeur(self, champ, val)
        contraintes = self.verification_contraintes(champ, widget)
        text_err = f"<span style='color: red'><b>Les valeurs saisies ne sont pas conformes aux contraintes :</b></span><br/><br/>"
        text_err += f"<span style='color: blue'><b>{champ}:</b></span><br/>{contraintes}<br/>"
        if contraintes:
            QMessageBox.warning(self, "Contraintes", text_err)
            widget.setText(self.dico_val_linedit[champ])
            widget.setStyleSheet(f"background-color: {self.color_btn_commun}")

    # slot bouton
    def bouton_sel(self, champ, val):
        self.set_color_btn(champ, val,self.color_btn_sel)

        # initialisation d'un dico pour gérer le changeattributs
        index_champs = self.layer.fields().indexOf(champ)
        self.widget_clique[index_champs] = val

    # slot combobox
    def combobox_sel(self,champ,val):
        # il faut initialiser tous les boutons en blanc
        self.set_all_btn_color(champ,None)

        # si l'item est vert, on ne modifie pas la couleur
        self.set_color_itemcombo(champ, val,self.color_btn_sel)

        # initialisation d'un dico pour gérer le changeattributs
        index_champs = self.layer.fields().indexOf(champ)
        self.widget_clique[index_champs] = val

    def explore_elements(self, elements, champ):
        for elem in elements:
            # if isinstance(elem, QgsAttributeEditorField):
            if elem.name() == champ:
                # 🔍 Récupère le champ réel depuis la couche
                idx = self.layer.fields().indexOf(champ)
                field = self.layer.fields().field(idx)
                constraints = field.constraints()
                # Récupère les infos de contraintes
                expression = constraints.constraintExpression()
                # print("Expression de contrainte :", expression or "(aucune)")
                return {"expression" : expression or ""}
        return None

    def contraintes_saisie(self,champ):
        form_config = self.layer.editFormConfig()
        return self.explore_elements(form_config.tabs(),champ)

    def verification_contraintes(self, champ, widget):
        contraintes = self.contraintes_saisie(champ)
        if not contraintes or not contraintes["expression"]:
            return
        valeur = widget.text().strip()
        expr_str = contraintes["expression"].replace(f'"{champ}"', '@value')
        # Crée l'expression QGIS
        expr = QgsExpression(expr_str)
        # Crée un contexte pour évaluer l'expression
        context = QgsExpressionContext()
        layer_scope = QgsExpressionContextUtils.layerScope(self.layer)
        context.appendScope(layer_scope)

        # ⚡ Ajout des variables dans le scope
        layer_scope.setVariable("value", valeur)  # @value
        layer_scope.setVariable("@value", valeur)  # pour les expressions qui utilisent @value
        layer_scope.setVariable(champ, valeur)  # si l'expression fait référence au champ par son nom

        res = expr.evaluate(context)
        if not res:
            print(f"⚠️ Valeur '{valeur}' invalide selon la contrainte : {expr.expression()}")
            return  expr.expression()
        else:
            print(f"✅ Valeur '{valeur}' valide selon la contrainte.")
            return  ""

    def valide_modif(self):
        # for linedit,valeur in self.dico_val_linedit.items():
        #     print(f"linedit avant modif = , {linedit} --{valeur}")

        contraintes = ""
        text_err = f"<span style='color: red'><b>Les valeurs saisies ne sont pas conformes aux contraintes :</b></span><br/><br/>"
        for champ,contraintes in self.get_contraintes.items():
            text_err += f"<span style='color: blue'><b>{champ}:</b></span><br/>{contraintes}<br/>"
        if contraintes:
            QMessageBox.warning(self, "Contraintes", text_err)
            return

        self.layer.startEditing()
        compteur = 0
        for sel in self.layer.selectedFeatures():
            for index_champ,nouvelle_valeur in self.widget_clique.items():
                ancienne_valeur_sel = sel.attribute(index_champ)
                if ancienne_valeur_sel != nouvelle_valeur:
                    print(f"VALIDATION : {ancienne_valeur_sel} --> {nouvelle_valeur}")
                    self.layer.changeAttributeValue(sel.id(), index_champ, nouvelle_valeur)
                    compteur += 1

        message = f"Les modifications ont été effectués sur : {compteur} entité(s)"
        self.iface.messageBar().pushMessage("Info", message, level=Qgis.Info, duration=5)

        self.widget_clique.clear()
        self.dico_val_linedit.clear()
        self.plugin.actualiserSelection()

    # ajoute les boutons dans l'interface en fonction du filtre
    def gestionfiltre(self):
        self.dlgFiltre = FiltreDialog(self.layer)
        if self.dlgFiltre.exec_() == QDialog.Accepted:
            # Récupère les filtres choisis par l'utilisateur
            self.dico_filtre = self.dlgFiltre.getcheckitem()
            # Rafraîchir les widgets selon les filtres
            self.add_widget_from_filtre()

    def apropos(self):
        dlgAProposDe = QDialog()
        loadUi(os.path.dirname(__file__) + "/aproposde.ui", dlgAProposDe)
        dlgAProposDe.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        dlgAProposDe.setWindowTitle(f"{TITRE} {VERSION}")
        dlgAProposDe.pushButtonAffichedoc.clicked.connect(afficheDoc)
        dlgAProposDe.exec_()




    def show_param(self):
        self.dlgParam = ParamDialog()
        # connecte le bouton OK du dialog à la mise à jour en direct
        self.dlgParam.pushButtonOk.clicked.connect(self.applique_parametres)
        self.dlgParam.show() #  seulement si l'utilisateur valide

    def applique_parametres(self):
        # recharge le dictionnaire mis à jour
        self.dico_param = self.dlgParam.dico_param
        self.nb_widget_par_ligne = self.dico_param.get("nb_btn_ligne", 3)
        self.color_btn_valider = self.dico_param.get("couleur_btn_valider", "#df920d")
        self.color_btn_sel = self.dico_param.get("couleur_btn_selection", "#2ab51a")
        self.color_btn_commun = self.dico_param.get("couleur_btn_commun", "#ff8080")
        self.taille_btn = self.dico_param.get("taille_btn", 30)

        # on recharge les btn pour prendre en compte le changement du nb de btn par ligne et les couleurs
        self.plugin.add_all_widget()
        # mettre à jour à la volée la couleur du bouton valider les modifs
        self.btn_valider.setStyleSheet(f"font-weight: bold;background-color: {self.color_btn_valider}")

        self.dlgParam.sauve_param_json()
        # attendre la fin des calculs puis Rafraîchir l'interface
        QTimer.singleShot(0, self.plugin.actualiserSelection)




