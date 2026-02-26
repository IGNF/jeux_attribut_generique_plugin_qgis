from qgis.core import QgsExpressionContext, QgsExpressionContextUtils, QgsExpression




# ========================================
# LECTURE DU FORMULAIRE D'ATTRIBUTS
# ========================================

# retourne les valeurs par defaut du formulaire d'attributs
def getValdefautForm(layer, champ):
    idx = layer.fields().indexOf(champ)
    if idx == -1:
        return None
    field = layer.fields().field(idx)
    valdefaut = field.defaultValueDefinition()
    # oin ne retient que si la valeur est appliqué pour mise à jour et non pour creation
    if valdefaut.applyOnUpdate():
        return valdefaut.expression()
    return None


def getValdefautFormALLchamps(layer):
    dico = {}
    for field in layer.fields():
        valdefaut = getValdefautForm(layer, field.name())
        if valdefaut is not None and valdefaut != "":
            dico[field.name()] = valdefaut
    return dico


# retourne les contraintes de saisie du formulaire d'attributs
def getContrainteForm(layer, champ):
    idx = layer.fields().indexOf(champ)
    if idx == -1:
        return None
    field = layer.fields().field(idx)
    constraints = field.constraints()
    return constraints.constraintExpression()

# retourne TRUE si le champ est readonly , FALSE sinon
def isreadonly(layer,champ):
    index = layer.fields().indexOf(champ)
    form_config = layer.editFormConfig()
    read_only = form_config.readOnly(index)
    return read_only

# def verification_valeur_defaut_formulaire(layer, champ):
#     valdefaut = getValdefautForm(layer, champ)
#     print("valeur par défaut = ", valdefaut)
#     if not valdefaut:
#         return

# Evalue la contrainte de saisie
def verification_contraintes_formulaire(layer, champ, widget):
    contraintes = getContrainteForm(layer, champ)
    if not contraintes:
        return
    # supp des espaces en debut de chaine
    valeur = widget.text().strip()

    expr_str = contraintes.replace(f'"{champ}"', '@value')
    # Crée l'expression QGIS
    expr = QgsExpression(expr_str)
    # Crée un contexte pour évaluer l'expression
    context = QgsExpressionContext()
    layer_scope = QgsExpressionContextUtils.layerScope(layer)
    context.appendScope(layer_scope)

    # Ajout des variables dans le scope
    layer_scope.setVariable("value", valeur)  # @value
    layer_scope.setVariable(champ, valeur)  # si l'expression fait référence au champ par son nom

    res = expr.evaluate(context)
    if not res:
        # print(f"⚠️ Valeur '{valeur}' invalide selon la contrainte : {expr.expression()}")
        return  expr.expression()
    else:
        # print(f"✅ Valeur '{valeur}' valide selon la contrainte.")
        return  ""
