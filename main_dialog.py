from pathlib import Path

from qgis.PyQt.QtCore import QObject, QEvent, QSize, QDate, QTimer, QDateTime,QPoint
from qgis.PyQt.QtGui import QColor,QCursor
from qgis.PyQt.QtWidgets import (QFormLayout, QHBoxLayout, QVBoxLayout, QFrame, QInputDialog, QAbstractSpinBox,
                                 QListView,QApplication)
from qgis.PyQt.uic import loadUi
from qgis.core import  Qgis
from qgis.utils import plugins

from .filtre import FiltreDialog
from .param import ParamDialog
from .fonction import *
from .formulaire import *
from .mapping_version import *

# class ChangeDateUtilisateur(QObject):
#     def __init__(self, class_parent):
#         super().__init__()
#         self.class_parent = class_parent
#
#     def eventFilter(self, obj, event):
#         # evenement pour detecter uniquement les changements de dates par utilisateurs
#         # et non par programmation
#         # if isinstance(obj, QDateEdit):
#         if isinstance(obj, QgsDateTimeEdit):
#             if event.type() in (QEvent.KeyPress,
#                                 QEvent.MouseButtonPress,
#                                 QEvent.Wheel):  # molette
#                 # QTimer pour eviter le "clic de retard"
#                 QTimer.singleShot(100, lambda: self.class_parent.on_user_date_changed(obj))
#                 # obj.user_edit = True
#         return False

class FiltreClicDroit(QObject):
    def __init__(self, class_parent):
        super().__init__()
        self.class_parent = class_parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == LeftButton:
            self._dragging = False
            self.widget_avant_move = obj
            self._press_pos = event.pos()

            # clic gauche sur un bouton
            if isinstance(obj, QPushButton):
                self.type_drag = "button"

            # # clic gauche sur un item du combobox
            elif isinstance(obj, QWidget):
                view = obj.parentWidget()
                while view and not hasattr(view, "indexAt"):
                    view = view.parentWidget()
                if view:
                    combo = view.parent()
                    while combo and not isinstance(combo, QComboBox):
                        combo = combo.parent()
                    if combo:
                        self.type_drag = "combo"
                        self.combo_source = combo
                    index = view.indexAt(event.pos())
                    if index.isValid():
                        self.class_parent.index_combo = index
                        self.class_parent.combo_pos_avant_move = (self.class_parent.get_position_combo(combo))
                        self.class_parent.combo_init_index = index.row()
                        self.class_parent.combo_avant_move_text = index.data()
            return False

        if event.type() == QEvent.MouseMove:
            if getattr(self, "_press_pos", None):
                if (event.globalPos() - self._press_pos).manhattanLength() > QApplication.startDragDistance():

                    # recuperation du widget sous la souris
                    widget_sous_souris = QApplication.widgetAt(event.globalPos())

                    # on bouge un bouton sur une autre ligne ->
                    # - on affiche le fantome_interdit
                    # - on masque le fantome_btn et on return False
                    if self.type_drag == "button":
                        pos_init = self.class_parent.get_position_btn(obj)
                        pos_final = self.class_parent.get_position_btn(widget_sous_souris)
                        if pos_init is not None and pos_final is not None:
                            # si ligne différente ...
                            if pos_init[0] != pos_final[0]:
                                print(f"deplacement interdit pour btn : {pos_init[0]} --> {pos_final[0]}")
                                self.class_parent._ghost.hide()
                                self.class_parent.show_fantome_interdit(event)
                                return False

                    # on bouge un item du combo sur une autre ligne ->
                    # - on affiche le fantome_interdit
                    # - on masque le fantome_btn et on return False
                    if self.type_drag == "combo" and self.combo_source is not None:
                        pos_init = self.class_parent.get_position_combo(self.combo_source)
                        pos_final = self.class_parent.get_position_btn(widget_sous_souris)

                        if pos_init is not None and pos_final is not None:
                            if pos_init[0] != pos_final[0]:
                                self.class_parent._ghost_combo.hide()
                                self.class_parent.show_fantome_interdit(event)
                                return False


                    # # on bouge un item du combo sur une autre ligne ->
                    # # - on affiche le fantome_interdit
                    # # - on masque le fantome_combo et on return False
                    # elif isinstance(obj, QListView):
                    #     print("on bouge le combo")
                    # pos_init = self.class_parent.get_position_combo(obj)
                    # pos_final = self.class_parent.get_position_combo(widget_sous_souris)
                    # if pos_init is not None and pos_final is not None:
                    #     # si ligne différente ...
                    #     if pos_init[0] != pos_final[0]:
                    #         print(f"deplacement interdit pour btn : {pos_init[0]} --> {pos_final[0]}")
                    #         self.class_parent._ghost_combo.hide()
                    #         self.class_parent.show_fantome_interdit(event)
                    #         return False



                    # Traitement par rapport aux WIDGETS SURVOLES
                    self._dragging = True
                    # on survol un bouton
                    if isinstance(widget_sous_souris, QPushButton):
                        if self.type_drag == "button":
                            self.class_parent.show_fantome_btn(event,obj)
                        elif self.type_drag == "combo":
                            self.class_parent.show_fantome_item_combo(event, obj)
                        self.class_parent._ghost_interdit.hide()

                    # on survol un label (label fantome)
                    elif isinstance(widget_sous_souris,QLabel):
                        self.class_parent.show_fantome_interdit(event)
                        self.class_parent._ghost.hide()

                    # on survol un item du combo
                    elif widget_sous_souris.parent() and isinstance(widget_sous_souris.parent(), QListView): #combobox
                        self.class_parent.show_fantome_item_combo(event,obj)
                        self.class_parent._ghost_interdit.hide()

                    # on survol le combo
                    elif isinstance(widget_sous_souris, QComboBox):
                        self.class_parent.show_fantome_btn(event, obj)
                        self.class_parent._ghost_interdit.hide()

                    # on survol autre chose (fond de l'interface par exemple)
                    else:
                        self.class_parent.show_fantome_interdit(event)
                        self.class_parent._ghost.hide()
                        self.class_parent._ghost_combo.hide()
            return False

        if event.type() == QEvent.MouseButtonRelease and event.button() == LeftButton:
            if getattr(self, "_dragging", False):
                widget_apres_move = QApplication.widgetAt(event.globalPos())
                if isinstance(obj, QPushButton):
                    self.class_parent.relache_clic_gauche_btn(self.widget_avant_move, widget_apres_move)
                elif isinstance(obj, QWidget):
                    self.class_parent.relache_clic_gauche_combo(widget_apres_move)

            self._dragging = False
            self._press_pos = None
            self.widget_avant_move = None
            self.class_parent._ghost.hide()
            self.class_parent._ghost_combo.hide()
            self.class_parent._ghost_interdit.hide()
        return False

class MainDialog(QDialog):

    def __init__(self ,iface,layer,plugin,parent=None):
        super().__init__(parent)

        # =====================================================
        # image fantôme qui suit la souris lors du drag and drop des boutons
        self._ghost = QLabel(None)
        self._ghost.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._ghost.setWindowFlags(ToolTip | FramelessWindowHint)
        self._ghost.setScaledContents(True)
        self._ghost.setStyleSheet("""
            background-color: rgb(30, 144, 255);  /* bleu semi-transparent */
            border: 1px solid blue;
            padding: 1px;
        """)
        self._ghost.hide()

        # =================================
        # image fantôme pour l'item d'un combo
        self._ghost_combo = QLabel(None)
        self._ghost_combo.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._ghost_combo.setWindowFlags(ToolTip | FramelessWindowHint)
        self._ghost_combo.setScaledContents(True)
        self._ghost_combo.setStyleSheet("""
            color: black;
            border: 1px solid blue;
            padding: 5px;
        """)
        self._ghost_combo.hide()
        # ===================================

        # ===================================
        # image fantôme interdit
        self._ghost_interdit = QLabel(None)
        # éviter de détecter le survol de la souris sur le qlabel fantôme, prendre que les btn en compte
        self._ghost_interdit.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._ghost_interdit.setWindowFlags(ToolTip | FramelessWindowHint)
        self._ghost_interdit.setScaledContents(True)
        self.path_ghost_interdit = Path(__file__).parent / "icons" / "ghost_interdit.PNG"
        icon = QIcon(str(self.path_ghost_interdit))
        pixmap = icon.pixmap(30, 30)
        self._ghost_interdit.setPixmap(pixmap)
        self._ghost_interdit.hide()
        # =============================================

        self.combo_pos_avant_move = None
        self.combo_avant_move_text = None

        self.get_contraintes = {}
        self.dlgFiltre = None
        self.dico_filtre = None

        # avant modif
        self.dico_val_linedit = {}

        self.plugin = plugin
        self.iface = iface
        self.layer = layer

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
        self.taille_font = self.dico_param.get("taille_btn", TAILLE_FONT_DEFAUT)

        self.setWindowTitle(f"{TITRE}")
        self.setWindowIcon(QIcon(PATHICON))
        self.setWindowFlags(Window | WindowCloseButtonHint)

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
        self.btn_apropos = QPushButton()
        self.btn_apropos.setIcon(QIcon(PATHICON_APROPOS))
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

        # ajout des 2 layouts (permanent et layout des btn) séparés par une ligne
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
        self.btn_valider.setFocusPolicy(NoFocus)
        self.btn_filtre.clicked.connect(self.gestionfiltre)
        self.btn_filtre.setFocusPolicy(NoFocus)
        self.btn_apropos.clicked.connect(self.apropos)
        self.btn_apropos.setFocusPolicy(NoFocus)
        self.btn_param.clicked.connect(self.show_param)
        self.btn_param.setFocusPolicy(NoFocus)
        self.btn_importer.clicked.connect(lambda:importer_json(self)) # self -> pour lier le qmessage au dlg pour passer devant
        self.btn_importer.setFocusPolicy(NoFocus)
        self.btn_exporter.clicked.connect(lambda:exporter_json(self))
        self.btn_exporter.setFocusPolicy(NoFocus)
        self.btn_sens_num.clicked.connect(self.affiche_sens_num)
        self.btn_sens_num.setFocusPolicy(NoFocus)

    def affiche_sens_num(self):
        try:
            processing_plugin = plugins[PLUGIN_CHE_SENS_NUM]
            processing_plugin.run()
        except KeyError:
            QMessageBox.warning(None, "Attention",
                f"Le plugin {PLUGIN_CHE_SENS_NUM} n'est pas installé ou pas activé\n"
                f"- Veuillez l'activer dans le menu \"Installer/Gérer les extensions de QGIS\"")

    def che_plus_court(self):
        try:
            processing_plugin = plugins[PLUGIN_CHE_PLUS_COURT]
            processing_plugin.run()
        except KeyError:
            QMessageBox.warning(None, "Attention",
                f"Le plugin {PLUGIN_CHE_PLUS_COURT} n'est pas installé ou pas activé\n"
                f"- Veuillez l'activer dans le menu \"Installer/Gérer les extensions de QGIS\"")
        QTimer.singleShot(0, self.plugin.actualiserSelection)

    def show_fantome_btn(self,event,obj):
        pix = obj.grab().scaled(obj.width(),obj.height() )
        self._ghost.setPixmap(pix)
        self._ghost.move(event.globalPos() - QPoint(10, int(pix.height()/2)))
        self._ghost.show()

    def show_fantome_item_combo(self,event,obj):
        # on utilise la valeur mémorisée au clic
        valeur = self.combo_avant_move_text
        if not valeur:
            return
        self._ghost_combo.setText(str(valeur))
        self._ghost_combo.adjustSize()
        self._ghost_combo.raise_()

        # position suit juste la souris
        self._ghost_combo.move(QCursor.pos() - QPoint(10, 10))
        self._ghost_combo.show()

    def show_fantome_interdit(self, event):
        self._ghost_interdit.move(event.globalPos() - QPoint(15, 15))
        self._ghost_interdit.show()

    def relache_clic_gauche_combo(self,obj_sous_mouse):
        pos_final = self.get_position_btn(obj_sous_mouse)
        # si la position est en dehors du layout, on quitte
        if pos_final is None:
            return

        # on valide le déplacement uniquement sur la meme ligne
        if self.combo_pos_avant_move[0] != pos_final[0]:
            print("déplacement combo interdit : pas sur la même ligne")
            return

        valeur = self.combo_avant_move_text
        # rechercher dans le json le champ du combo avant le déplacement
        champ = self.get_champ_from_json(valeur)

        # TODO : optimise en ne chargeant que le layer concerné et pas tout le json (mais la fonction loadjson est faite pour charger tout le json et retourner que le layer concerné, à revoir si besoin)
        with open(PATHJSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        valeur_par_champ = data[self.layer.name()][champ]

        valeur_par_champ.remove(valeur)
        valeur_par_champ.insert(pos_final[1], valeur)

        # Sauvegarde du JSON complet (structure conservée)
        try:
            with open(PATHJSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f" Erreur sauvegarde JSON : {e}")

        self.plugin.dico_filtre = loadjson(self.layer.name())
        self.plugin.add_all_widget()
        QTimer.singleShot(0, self.plugin.actualiserSelection)


    def get_champ_from_json(self,valeur_recherche):
        data = loadjson(self.layer.name())
        for champ, valeurs in data.items():
            if isinstance(valeurs, list) and valeur_recherche in valeurs:
                return champ
        return None

    def relache_clic_gauche_btn(self, obj, obj_sous_mouse):
        pos_init = self.get_position_btn(obj)
        pos_final = self.get_position_btn(obj_sous_mouse)
        # si la position est en dehors du layout, on quitte
        if pos_final is None:
            return

        # on valide le déplacement uniquement sur la meme ligne
        if pos_init[0] != pos_final[0]:
            return

        # deplacement du bouton dans le json si le bouton est relaché sur un autre bouton
        with open(PATHJSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        champ = obj.property("champ")
        valeur = obj.property("valeur")
        valeur_par_champ = data[self.layer.name()][champ]
        valeur_par_champ.remove(valeur)
        # pos_final[1] --> 2ieme composante de coordonnées
        valeur_par_champ.insert(pos_final[1], valeur)

        # Sauvegarde du JSON complet (structure conservée)
        try:
            with open(PATHJSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f" Erreur sauvegarde JSON : {e}")

        # actualisation de l'interface
        self.plugin.dico_filtre = loadjson(self.layer.name())
        self.plugin.add_all_widget()
        QTimer.singleShot(0, self.plugin.actualiserSelection)

    def get_position_combo(self, combo):
        for ligne in range(self.formlayout.rowCount()):
            field_item = self.formlayout.itemAt(ligne,QFormLayout.FieldRole)
            if not field_item:
                continue
            layout = field_item.layout()
            if not layout:
                continue
            for col in range(layout.count()):
                widget = layout.itemAt(col).widget()
                if widget == combo:
                    return ligne, col
        return None

    def get_position_btn(self,obj):
        for ligne in range(self.formlayout.rowCount()):
            field_item = self.formlayout.itemAt(ligne,QFormLayout.FieldRole)
            if field_item is None:
                continue
            layout = field_item.layout()
            if layout is None:
                continue
            for col in range(layout.count()):
                widget = layout.itemAt(col).widget()
                if widget == obj:
                    return ligne, col
        return None

    def create_btn(self,champ,val,read_only):
        btn = QPushButton(str(val))
        font = btn.font()
        font.setPointSize(self.taille_font)
        btn.setFont(font)
        btn.setEnabled(not read_only)
        btn.setProperty("champ", champ)
        btn.setProperty("valeur", val)
        btn.setProperty("iswidgetjson", True)
        btn.setToolTip(str(val))
        btn.setFocusPolicy(NoFocus)

        # gestion clic droit
        btn.installEventFilter(self.filtre_clic_droit)
        btn.clicked.connect(lambda _, c=champ, v=val: self.bouton_sel(c, v))
        return btn

    def add_widget(self,champ,valeurs,typewidget):
        # formatage du nom des champs (suppr des _)
        text_label = champ.replace("_", " ").replace("l ", "l'").replace("d ", "d'").capitalize()
        champ_format = QLabel(text_label)
        champ_format.setStyleSheet("""
            color: #b63d3d;
            font-weight: bold;
        """)

        hlayout = QHBoxLayout()
        hlayout.setSpacing(1)

        # test si le champ est editable ou pas
        read_only = isreadonly(self.layer,champ)

        if typewidget == "DateTime":
            # widgdatetime = QDateTimeEdit()
            # widgdatetime = QDateEdit()
            widgdatetime = QgsDateTimeEdit()
            widgdatetime.setReadOnly(read_only)
            widgdatetime.setEnabled(not read_only)
            widgdatetime.setFixedWidth(180)
            widgdatetime.setDisplayFormat("dd.MM.yyyy")
            widgdatetime.setProperty("champ", champ)
            widgdatetime.setProperty("valeur", "")
            widgdatetime.setProperty("iswidgetjson", True)

            # désactive le bouton de valeur NULL
            widgdatetime.setAllowNull(False)

            # bloque la saisie direct dans le lineedit (clic, molette,fleche)
            widgdatetime.lineEdit().setReadOnly(True)
            widgdatetime.setButtonSymbols(QAbstractSpinBox.NoButtons)
            widgdatetime.setFocusPolicy(NoFocus)
            widgdatetime.wheelEvent = lambda event: None

            # widgdatetime.editingFinished.connect(lambda c=champ: self.on_perte_focus_date(c))
            # widgdatetime.installEventFilter(self.date_changed)
            # widgdatetime.valueChanged.connect(lambda v, c=champ:  self.on_user_date_changed(c, v))

            # l'evenement est sur le calendrier, pas directement sur le widget
            cal = widgdatetime.calendarWidget()
            cal.clicked.connect(lambda v, c=champ:  self.on_user_date_changed(c, v))

            hlayout.addWidget(widgdatetime)

        if typewidget == "TextEdit":
            lineedit = QLineEdit()
            font = lineedit.font()
            font.setPointSize(self.taille_font)
            lineedit.setFont(font)
            # on désactive le menu contextuel d'un clic droit par défaut sur un lineedit
            lineedit.setContextMenuPolicy(NoContextMenu)
            lineedit.setReadOnly(read_only)
            lineedit.setEnabled(not read_only)
            lineedit.setFixedWidth(180)
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
            # boucle sur 0 --> self.nb_widget_par_ligne
            for val in valeurs[:self.nb_widget_par_ligne]:
                btn = self.create_btn(champ,val,read_only)
                hlayout.addWidget(btn)

            if len(valeurs) == self.nb_widget_par_ligne + 1:
                val = valeurs[-1]
                btn = self.create_btn(champ, val, read_only)
                hlayout.addWidget(btn)

            elif len(valeurs) > self.nb_widget_par_ligne + 1:
                combo = QComboBox()
                combo.setEnabled(not read_only)
                font = combo.font()
                font.setPointSize(self.taille_font)
                combo.setFont(font)

                combo.addItems([str(val) for val in valeurs[self.nb_widget_par_ligne:]])

                # combo.setFixedHeight(self.taille_btn)
                combo.setProperty("champ", champ)
                combo.setProperty("valeur", combo.currentText())
                combo.setProperty("iswidgetjson", True)
                # on stock le combo
                self.combo_widgets[champ] = combo
                # combo.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
                hlayout.addWidget(combo)
                combo.setFocusPolicy(NoFocus)

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
                # si c'est un bouton
                if isinstance(widget, QPushButton):
                    self.set_all_item_color(champ,None)
                    self.set_color_btn(champ,val_unique,self.color_btn_commun)
                # si c'est un combobox
                if isinstance(widget, QComboBox):
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

                if isinstance(widget, QgsDateTimeEdit):
                # if isinstance(widget, QDateEdit):
                    # sans les décimales des secondes
                    only_date = val_unique.split(" ")[0]
                    date_format = "yyyy-MM-dd"
                    qdt = QDateTime.fromString(only_date, date_format)
                    widget.setDateTime(qdt)
                    widget.setStyleSheet(f"background-color: {self.color_btn_commun}")

            # Sinon (plusieurs valeurs différentes)
            else:
                widget = get_widget_by_champ_valeur(self, champ)
                if isinstance(widget, QLineEdit):
                    widget.setText("***")  # afficher *** pour ambiguïté
                    # widget.setStyleSheet("font-weight: bold;background-color: None")
                    widget.setStyleSheet("background-color: None")
                    self.dico_val_linedit[champ] = "***"

                # elif isinstance(widget, QDateEdit):
                elif isinstance(widget, QgsDateTimeEdit):
                    widget.setDateTime(QDateTime(QDate(1900, 1, 1)))
                    # widget.setDateTime(QDateTime())  # valeur nulle
                    # widget.setNullRepresentation("***")
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
                model.setData(index, QColor(color), BackgroundRole)

    # on modifie la couleur SAUF si l'item a la couleur : self.color_btn_commun'
    def set_color_itemcombo(self,champ,val=None,color = None):
        # on initilaise tous les item a color blanc
        combo = get_widget_by_champ_valeur(self, champ,val)
        if combo is None:
            return
        model = combo.model()

        for i in range(model.rowCount()):
            index = model.index(i, 0)
            texte = model.data(index)
            current_color = model.data(index, BackgroundRole)
            if current_color == QColor(self.color_btn_commun):
                continue
            model.setData(index, QColor("White"), BackgroundRole)
            # if texte == val and style != f"background-color: {self.color_btn_commun}":
            if texte == val :
                model.setData(index, QColor(color), BackgroundRole)
            else:
                model.setData(index, QColor("White"), BackgroundRole)

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

        # test
        # regex_str = "^(0[1-9]|2([AB]|[1-9])|(1|[3-8])[0-9]|9[0-5])[0-9]{3}$"
        # regex_str = "^(0[1-9]|[1-8][0-9]|9[0-5]|2A|2B)[0-9]{3}|97[1-8][0-9]{2}|9841[1-5]|99(109|130|131|134|127|137|138|140|437|416|445|132)$"
        # regex_str = "length(insee_commune_gauche) <= 5"
        # is_valid,type_chaine = type_de_chaine(regex_str)
        # print(type_chaine)

        # erreur,text = verifier_regex(val,regex_str)
        # print(val , ": ",text)

        widget = get_widget_by_champ_valeur(self, champ, val)
        # contraintes = self.verification_contraintes(champ, widget)
        contraintes = verification_contraintes_formulaire(self.layer, champ, widget)
        if contraintes:
            contraintes = contraintes.replace("@value", champ)
            dlg_affichercontraintes(contraintes, "Contraintes")
            widget.setText(self.dico_val_linedit[champ])
            widget.setStyleSheet(f"background-color: {self.color_btn_commun}")

            # remettre dans : self.widget_clique[index_champs]
            # l'ancienne valeur
            index_champs = self.layer.fields().indexOf(champ)
            self.widget_clique[index_champs] = self.dico_val_linedit[champ]

    def on_user_date_changed(self, champ, val):
        widget = get_widget_by_champ_valeur(self, champ)
        qdt = widget.dateTime()
        index_champs = self.layer.fields().indexOf(champ)
        self.widget_clique[index_champs] = qdt.toString("yyyy-MM-dd")
        widget.setStyleSheet(f"background-color: {self.color_btn_sel}")

    # def on_user_date_changed(self,obj):
    #     print("user_date_changed")
    #     champ = obj.property("champ")
    #     widget = get_widget_by_champ_valeur(self, champ)
    #
    #     qdt = widget.dateTime()
    #     index_champs = self.layer.fields().indexOf(champ)
    #     self.widget_clique[index_champs] = qdt.toString("yyyy-MM-dd")
    #     widget.setStyleSheet(f"background-color: {self.color_btn_sel}")
    #     print(widget.lineEdit().text())

    # def on_perte_focus_date(self, champ):
        # widget = get_widget_by_champ_valeur(self, champ)
        # widget.setStyleSheet(f"background-color: {self.color_btn_sel}")

        # récupérer la QDateTime courante
        # widget = get_widget_by_champ_valeur(self, champ)
        # qdt = widget.dateTime()
        # index_champs = self.layer.fields().indexOf(champ)
        # self.widget_clique[index_champs] = qdt.toString("yyyy-MM-dd")


    # slot bouton
    def bouton_sel(self, champ, val):
        self.set_color_btn(champ, val, self.color_btn_sel)

        # initialisation d'un dico pour gérer le changeattributs
        index_champs = self.layer.fields().indexOf(champ)
        self.widget_clique[index_champs] = val

        # lecture des valeurs par defaut du formulaire
        valdefaut = getValdefautForm(self.layer,champ)
        # print(valdefaut)

        # test : recuperation des valeurs par defauts sur tous les champs
        dico = getValdefautFormALLchamps(self.layer)
        # print(dico.keys())


    # slot combobox
    def combobox_sel(self,champ,val):
        # il faut initialiser tous les boutons en blanc
        self.set_all_btn_color(champ,None)

        # si l'item est vert, on ne modifie pas la couleur
        self.set_color_itemcombo(champ, val,self.color_btn_sel)

        # initialisation d'un dico pour gérer le changeattributs
        index_champs = self.layer.fields().indexOf(champ)
        self.widget_clique[index_champs] = val

    def valide_modif(self):
        # force la perte du focus des QDateTimeEdit pour récupérer leurs valeurs
        # self.focusWidget().clearFocus()

        # TODO a faire : si la date est 1900.... on ne modifie pas

        self.layer.startEditing()
        compteur = 0
        for sel in self.layer.selectedFeatures():
            for index_champ,nouvelle_valeur in self.widget_clique.items():
                ancienne_valeur_sel = sel.attribute(index_champ)
                if ancienne_valeur_sel != nouvelle_valeur:
                    # print(f"{ancienne_valeur_sel}-->{nouvelle_valeur}")
                    self.layer.changeAttributeValue(sel.id(), index_champ, nouvelle_valeur)
                    compteur += 1

        if (compteur !=0):
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
            QTimer.singleShot(0, self.plugin.actualiserSelection)

    def apropos(self):
        dlgAProposDe = QDialog()
        loadUi(os.path.dirname(__file__) + "/aproposde.ui", dlgAProposDe)
        dlgAProposDe.setWindowFlags(WindowStaysOnTopHint | WindowCloseButtonHint)
        dlgAProposDe.setWindowTitle(f"{TITRE}")
        dlgAProposDe.pushButtonAffichedoc.clicked.connect(afficheDoc)
        dlgAProposDe.exec_()

    def show_param(self):
        self.dlgParam = ParamDialog()
        # connecte le bouton OK du dialog à la mise à jour en direct
        self.dlgParam.pushButtonOk.clicked.connect(self.applique_parametres)
        self.dlgParam.exec_()

    def applique_parametres(self):
        # recharge le dictionnaire mis à jour
        self.dico_param = self.dlgParam.dico_param
        self.nb_widget_par_ligne = self.dico_param.get("nb_btn_ligne", 3)
        self.color_btn_valider = self.dico_param.get("couleur_btn_valider", "#df920d")
        self.color_btn_sel = self.dico_param.get("couleur_btn_selection", "#2ab51a")
        self.color_btn_commun = self.dico_param.get("couleur_btn_commun", "#ff8080")
        self.taille_font = self.dico_param.get("taille_btn", TAILLE_FONT_DEFAUT)

        # on recharge les btn pour prendre en compte le changement du nb de btn par ligne et les couleurs
        self.plugin.dico_filtre = loadjson(self.layer.name())
        self.plugin.add_all_widget()
        # mettre à jour à la volée la couleur du bouton valider les modifs
        self.btn_valider.setStyleSheet(f"font-weight: bold;background-color: {self.color_btn_valider}")

        self.dlgParam.sauve_param_json()
        # attendre la fin des calculs puis Rafraîchir l'interface
        QTimer.singleShot(0, self.plugin.actualiserSelection)




