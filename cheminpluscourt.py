from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsPointXY, QgsField, QgsCoordinateReferenceSystem, \
    QgsFeatureRequest, QgsFeature, QgsProcessingFeatureSourceDefinition, QgsProcessingException,QgsCoordinateTransform
from qgis.PyQt.QtCore import QVariant, Qt
from qgis.PyQt.QtGui import QGuiApplication

import time
from qgis import processing

from .fonction import afficheerreur
from .constante import *


# from .change_attribut_hydro_dialog import changeAttributDialog

def definiProjectionProjet(idproj):
    projection_epsg = idproj
    crs = QgsCoordinateReferenceSystem(projection_epsg)
    project = QgsProject.instance()
    project.setCrs(crs)


class cheminpluscourt:

    def selectionEntitesFromZoom(self):
        # selection des entités du memory layer compris dans la zone ecran
        rect = self.iface.mapCanvas().extent()
        request = QgsFeatureRequest(rect)
        request.setFlags(QgsFeatureRequest.ExactIntersect)
        listid = []
        for f in self.layer.getFeatures(request):
            listid.append(f.id())
        self.layer.selectByIds(listid)

    def creerLayerZoneEcran(self):
        projectionLayer = self.layer.crs()
        champs = [QgsField("cleabs", QVariant.Int)]
        layer_ecran = QgsVectorLayer("LineStringZ?crs=" + projectionLayer.authid(), "Layer ecran", "memory")
        layer_ecran.dataProvider().addAttributes(champs)
        layer_ecran.updateFields()
        QgsProject.instance().addMapLayer(layer_ecran)
        return layer_ecran

    def addEntitesToLayer(self, layer_zoom):
        selection = self.layer.selectedFeatures()
        ident = 0
        layer_zoom.startEditing()
        for entites in selection:
            nouvelle_entite = QgsFeature()
            nouvelle_entite.setGeometry(entites.geometry())  # Définir la géométrie de la nouvelle entité
            nouvelle_entite.setAttributes([selection[ident].id()])
            layer_zoom.addFeature(nouvelle_entite)
            ident = ident + 1
        layer_zoom.commitChanges()

    def cheminpluscourt(self):

        projectionLayer = self.layer.crs()
        projet = QgsProject.instance()
        projectionProjet = projet.crs()

        # on modifie la projection pour faire correspondre à celle du layer
        definiProjectionProjet(projectionLayer)

        start_time = time.time()

        QGuiApplication.setOverrideCursor(Qt.WaitCursor)

        # sauvegarde des id du troncon initial et final
        objetsselectionlayerini = self.layer.selectedFeatures()
        print(self.layer.selectedFeatureCount())

        # creation du layer zone ecran
        layerZoom = self.creerLayerZoneEcran()

        # copie des entités de la couche hydro dans la zone ecran
        self.selectionEntitesFromZoom()

        # ajout des entités selectionnés
        self.addEntitesToLayer(layerZoom)

        # re selection du troncon initial et final sur le layer
        self.layer.removeSelection()
        self.layer.select(objetsselectionlayerini[0].id())
        self.layer.select(objetsselectionlayerini[1].id())

        # intersection des 2 couches pour selectionner les 2 troncons sur le layer zoom
        processing.run("qgis:selectbylocation",
                       {'INPUT': layerZoom,
                        'PREDICATE': [6],
                        # 'INTERSECT': self.layer,

                        'INTERSECT': QgsProcessingFeatureSourceDefinition(self.layer.dataProvider().dataSourceUri(),
                                                                          selectedFeaturesOnly=True),
                        'METHOD': 0})

        if layerZoom.selectedFeatureCount() != 2:
            afficheerreur("Les tronçons de depart et d'arrivée doivent être visible à l'ecran")
            QgsProject.instance().removeMapLayer(layerZoom)
            # apres traitement on remet la projection du projet initial
            definiProjectionProjet(projectionProjet)
            QGuiApplication.restoreOverrideCursor()
            return

        # definition du point de depart et du point d'arrivé
        objetsselection = layerZoom.selectedFeatures()
        geom1 = objetsselection[0].geometry()
        geom2 = objetsselection[1].geometry()
        # premier point des lignes
        point_depart = QgsPointXY(geom1.vertexAt(0))
        point_final = QgsPointXY(geom2.vertexAt(0))

        try:
            resultat = processing.run(
                "native:shortestpathpointtopoint",
                {
                    "INPUT": layerZoom,
                    "START_POINT": point_depart,
                    "END_POINT": point_final,
                    "STRATEGY": 0,  # 0:plus court  1:plus rapide
                    "OUTPUT": "memory:chemin le plus court",
                }
            )
            couche_resultante = resultat["OUTPUT"]
            QgsProject.instance().addMapLayer(couche_resultante)
        except QgsProcessingException as qgs_ex:
            QgsProject.instance().removeMapLayer(layerZoom)
            afficheerreur(str(qgs_ex), "Erreur QGIS Processing :")
            QGuiApplication.restoreOverrideCursor()
            # apres traitement, on remet la projection du projet initial
            definiProjectionProjet(projectionProjet)
            return
        except Exception as e:
            afficheerreur(str(e), "Erreur générale :")
            QgsProject.instance().removeMapLayer(layerZoom)
            # apres traitement on remet la projection du projet initial
            definiProjectionProjet(projectionProjet)
            QGuiApplication.restoreOverrideCursor()

        # intersection de la couche hydro avec la couche temporaire pour selectionner le chemin le plus court
        # sur la couche hydro
        processing.run("qgis:selectbylocation",
                       {'INPUT': self.layer, 'PREDICATE': [6], 'INTERSECT': couche_resultante, 'METHOD': 0, })
        # on ajoute à la selection le premier et le dernier troncon pour regler le pb d'effet de bord
        self.layer.selectByIds([objetsselectionlayerini[0].id()], QgsVectorLayer.AddToSelection)
        self.layer.selectByIds([objetsselectionlayerini[1].id()], QgsVectorLayer.AddToSelection)


        distance = self.get_longueur_iti(self.layer.selectedFeatures(),self.layer)
        print(f"La distance totale est de {int(distance)} métres")

        # supprimer la couche temporaire apres la selectionbylocation
        QgsProject.instance().removeMapLayer(couche_resultante)
        QgsProject.instance().removeMapLayer(layerZoom)


        # apres traitement on remet la projection du projet initial
        definiProjectionProjet(projectionProjet)

        QGuiApplication.restoreOverrideCursor()


        # end_time = time.time()
        # temps_ecoule = end_time - start_time
        # print(f"traitement en {temps_ecoule:.2f} sec")

    def get_longueur_iti(self,selection,layer):
        longueur = 0
        # projection sur une surface plane pour recuperer la longueur en métres.
        crs = QgsCoordinateReferenceSystem("EPSG:3857")
        transformer = QgsCoordinateTransform(layer.crs(), crs, QgsProject.instance())
        for feature in selection:
            geometry = feature.geometry()
            geometry.transform(transformer)
            longueur += geometry.length()
        return longueur


    def __init__(self, iface, layer):
        self.iface = iface
        self.layer = layer
