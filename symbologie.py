from PyQt5.QtGui import QColor
from qgis._core import QgsSimpleMarkerSymbolLayerBase, QgsSingleSymbolRenderer, QgsRuleBasedRenderer
from qgis.core import QgsRendererCategory, QgsCategorizedSymbolRenderer,QgsSimpleMarkerSymbolLayer, QgsSymbol, QgsWkbTypes, QgsMarkerLineSymbolLayer


def init_symbole():
    # Créer le triangle comme SimpleMarkerLayer
    triangle_layer = QgsSimpleMarkerSymbolLayer()
    triangle_layer.setShape(QgsSimpleMarkerSymbolLayer.Triangle)
    triangle_layer.setColor(QColor(0, 0, 255))
    triangle_layer.setSize(2)
    triangle_layer.setAngle(90)

    # Créer un QgsSymbol pour le MarkerLine
    triangle_symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.PointGeometry)
    triangle_symbol.deleteSymbolLayer(0)  # supprime le SimpleMarker par défaut
    triangle_symbol.appendSymbolLayer(triangle_layer)

    ml = QgsMarkerLineSymbolLayer()
    ml.setSubSymbol(triangle_symbol)  # ⚡ ici on passe un QgsSymbol
    ml.setPlacement(QgsMarkerLineSymbolLayer.Interval)
    ml.setInterval(20)
    ml.setOffset(0)
    return ml

def add_symb_sens_num(layer):
    renderer = layer.renderer()

    if renderer.type() == "singleSymbol":
        ml = init_symbole()
        # Ajouter la MarkerLine au symbole existant
        sym = renderer.symbol().clone()
        sym.appendSymbolLayer(ml)

        layer.setRenderer(QgsSingleSymbolRenderer(sym))
        layer.setCustomProperty("extra_triangle_single",sym.symbolLayerCount() - 1)

    # on supprime le dernier ajouté
    # il correspond à celui ajouté dans add_symb_sens_nul
    elif renderer.type() == "RuleRenderer":
        print("ON EST DANS UN RuleRenderer")
        root = renderer.rootRule().clone()
        rules_to_process = [root]
        while rules_to_process:
            rule = rules_to_process.pop()
            sym = rule.symbol()
            if sym:
                sym = sym.clone()
                ml = init_symbole()
                sym.appendSymbolLayer(ml)
                rule.setSymbol(sym)
            rules_to_process.extend(rule.children())
        layer.setRenderer(QgsRuleBasedRenderer(root))

    elif renderer.type() == "categorizedSymbol":
        new_categories = []
        for cat in renderer.categories():
            sym = cat.symbol().clone()  # cloner le symbole existant
            ml = init_symbole()
            # Ajouter la MarkerLine au symbole existant
            sym.appendSymbolLayer(ml)
            # Stocker un identifiant pour suppression future
            layer.setCustomProperty(f"categorie_{cat.value()}", sym.symbolLayerCount() - 1)
            # Nouvelle catégorie
            new_cat = QgsRendererCategory(cat.value(), sym, cat.label())
            new_categories.append(new_cat)

        # Appliquer le nouveau renderer
        new_renderer = QgsCategorizedSymbolRenderer(renderer.classAttribute(), new_categories)
        layer.setRenderer(new_renderer)

        print(f"new_categories : {new_categories}")
    layer.triggerRepaint()


def suppr_symb_sens_num(layer):
    renderer = layer.renderer()
    if renderer.type() == "singleSymbol":
        sym = renderer.symbol().clone()
        idx = layer.customProperty("extra_triangle_single", None)
        if idx is not None:
            idx = int(idx)
            if 0 <= idx < sym.symbolLayerCount():
                sym.deleteSymbolLayer(idx)
            layer.removeCustomProperty("extra_triangle_single")
        layer.setRenderer(QgsSingleSymbolRenderer(sym))

    elif renderer.type() == "RuleRenderer":
        root = renderer.rootRule().clone()
        rules_to_process = [root]
        while rules_to_process:
            rule = rules_to_process.pop()
            rule_sym = rule.symbol()
            if rule_sym:
                sym = rule_sym.clone()
                # Supprimer uniquement le dernier MarkerLine (le triangle ajouté)
                for i in reversed(range(sym.symbolLayerCount())):
                    sl = sym.symbolLayer(i)
                    if isinstance(sl, QgsMarkerLineSymbolLayer):
                        sym.deleteSymbolLayer(i)
                        break  # on supprime seulement le dernier
                rule.setSymbol(sym)
            rules_to_process.extend(rule.children())
        layer.setRenderer(QgsRuleBasedRenderer(root))

    elif renderer.type() == "categorizedSymbol":
        new_categories = []
        for cat in renderer.categories():
            sym = cat.symbol().clone()  # clone pour ne pas modifier l'original
            # Supprimer uniquement le dernier MarkerLine ajouté
            for i in reversed(range(sym.symbolLayerCount())):
                sl = sym.symbolLayer(i)
                if isinstance(sl, QgsMarkerLineSymbolLayer):
                    sym.deleteSymbolLayer(i)
                    break  # on supprime seulement le dernier ajouté
            # Recréer la catégorie avec le symbole modifié
            new_cat = QgsRendererCategory(cat.value(), sym, cat.label())
            new_categories.append(new_cat)
        # Recréer le renderer catégorisé
        new_renderer = QgsCategorizedSymbolRenderer(renderer.classAttribute(), new_categories)
        layer.setRenderer(new_renderer)

    layer.triggerRepaint()
