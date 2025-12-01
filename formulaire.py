from qgis._core import QgsExpressionContext, QgsExpressionContextUtils, QgsExpression
import re
import sre_parse
import sre_constants

# il faut installer au prealable le module regex (pip install regex)
# verifier sin on a bien va variable d'environnement PYTHONPATH
# avec la valeur : C:\blablabla\AppData\Roaming\Python\Python312\site-packages
import regex

# ========================================
# LECTURE DU FORMULAIRE D'ATTRIBUTS
# ========================================


import regex


def verifier_regex(valeur, motif):
    pattern = regex.compile(motif)
    m = pattern.fullmatch(valeur)
    if m:
        return True, "La valeur correspond est BONNE"

    # Match partiel
    m = pattern.match(valeur, partial=True)
    if m and m.partial:
        return False, f"Correspondance partielle jusqu’à la position {m.end()}, blocage ensuite"
    else:
        return False, "Le début ne correspond pas au regex"


def type_de_chaine(expr):
    # Liste des métacaractères typiques des regex
    metacaracteres = set("^$.*+?{}[]|\\")
    # Si la chaîne contient au moins un métacaractère → probablement un regex
    if any(c in metacaracteres for c in expr):
        try:
            re.compile(expr)
            return True,"regex"
        except re.error:
            return False,"expression (syntaxe invalide pour regex)"
    # Sinon, c'est juste une expression littérale
    return True,"expression"



# def expected_length(pattern):
#     """
#     Détermine la longueur min/max attendue par une regex
#     """
#     parsed = sre_parse.parse(pattern)
#
#     min_len = 0
#     max_len = 0
#
#     for token in parsed:
#         ttype, tvalue = token
#
#         if ttype in (sre_parse.LITERAL, sre_parse.IN, sre_parse.ANY):
#             min_len += 1
#             max_len += 1
#
#         elif ttype is sre_parse.SUBPATTERN:
#             sub_min, sub_max = expected_length_from_subpattern(tvalue[3])
#             min_len += sub_min
#             max_len += sub_max
#
#         elif ttype is sre_parse.MAX_REPEAT:
#             min_repeat, max_repeat, subp = tvalue
#             smin, smax = expected_length_from_subpattern(subp)
#             min_len += min_repeat * smin
#             max_len += (max_repeat if max_repeat != sre_parse.MAXREPEAT else min_repeat) * smax
#
#     return min_len, max_len
#
#
# def expected_length_from_subpattern(subpattern):
#     min_len = 0
#     max_len = 0
#     for t, v in subpattern:
#         if t in (sre_parse.LITERAL, sre_parse.IN, sre_parse.ANY):
#             min_len += 1
#             max_len += 1
#     return min_len, max_len
#
# def explain_regex(pattern, value):
#
#     # 1. longueur attendue
#     min_len, max_len = expected_length(pattern)
#
#     if len(value) < min_len or len(value) > max_len:
#         if min_len == max_len:
#             return f"{value} ❌ : longueur incorrecte (attendu {min_len}, trouvé {len(value)})"
#         else:
#             return f"{value} ❌ : longueur {len(value)} invalide (attendu entre {min_len} et {max_len})"
#
#     # 2. test global
#     if re.fullmatch(pattern, value):
#         return f"{value} ✅ valide"
#
#     # 3. test position par position
#     for i in range(1, len(value)+1):
#         if not re.match(pattern, value[:i]):
#             char = value[i-1]
#             if char.isdigit():
#                 t = "un chiffre"
#             elif char.isalpha():
#                 t = "une lettre"
#             else:
#                 t = "un caractère spécial"
#
#             return f"{value} ❌ : position {i}, caractère '{char}' invalide ({t} inattendu à cet endroit)"
#
#     return f"{value} ❌ : structure non conforme au motif"



# def explain_regex(pattern_txt, value):
#     """
#         Fonction générique pour diagnostiquer une valeur par rapport à une regex.
#         Fournit des messages spécifiques pour :
#         - longueur incorrecte
#         - caractère inattendu
#         - portion restante ne correspondant pas
#         """
#     try:
#         pattern = regex.compile(pattern_txt)
#     except Exception as e:
#         return f"Erreur de compilation de la regex : {e}"
#
#     # # Vérifier longueur si le pattern a une longueur exacte avec {n} répétitions ou longueur fixe
#     # import re
#     # length_exact = None
#     # m = re.search(r"\{(\d+)\}", pattern_txt)
#     # if m:
#     #     length_exact = int(m.group(1))
#     #     if len(value) != length_exact:
#     #         return f"{value} invalide ❌ : longueur incorrecte (attendu {length_exact}, trouvé {len(value)})"
#
#     # Test global
#     if pattern.fullmatch(value):
#         return f"{value} est valide ✅"
#
#     # Test caractère par caractère pour donner un message spécifique
#     for i, ch in enumerate(value):
#         # extraire le motif attendu pour cette position (approximatif)
#         subpattern = pattern_txt[i] if i < len(pattern_txt) else None
#         if subpattern:
#             # simple détection chiffre vs lettre vs autre
#             if subpattern in "0-9" and not ch.isdigit():
#                 return f"{value} invalide ❌ : caractère '{ch}' à la position {i + 1}, chiffre attendu"
#             if subpattern in "A-Z" and not ch.isupper():
#                 return f"{value} invalide ❌ : caractère '{ch}' à la position {i + 1}, lettre majuscule attendue"
#             if subpattern in "a-z" and not ch.islower():
#                 return f"{value} invalide ❌ : caractère '{ch}' à la position {i + 1}, lettre minuscule attendue"
#
#     # Si aucune erreur spécifique trouvée, retour général
#     return f"{value} invalide ❌ : ne correspond pas au motif global"



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

# def traduireRegEx(regex_txt):
#     parsed = sre_parse.parse(regex_txt)
#
#     def describe(parsed_list, indent=0):
#         desc = ""
#         prefix = "  " * indent
#
#         for token in parsed_list:
#             t_type, t_value = token
#
#             if t_type == sre_parse.LITERAL:
#                 desc += f"{prefix}- Caractère exact : '{chr(t_value)}'\n"
#
#             elif t_type == sre_parse.SUBPATTERN:
#                 desc += f"{prefix}- Groupe :\n"
#                 desc += describe(t_value[1], indent + 1)
#
#             elif t_type in (sre_parse.MAX_REPEAT, sre_parse.MIN_REPEAT):
#                 min_r, max_r, subpattern = t_value
#                 subdesc = describe(subpattern, indent + 1).strip()
#                 if min_r == max_r:
#                     desc += f"{prefix}- Répété exactement {min_r} fois :\n{subdesc}\n"
#                 else:
#                     desc += f"{prefix}- Répété {min_r} à {max_r} fois :\n{subdesc}\n"
#
#             elif t_type == sre_parse.IN:
#                 # Transformer les classes de caractères en français
#                 chars = []
#                 for c in t_value:
#                     if c[0] == sre_parse.RANGE:
#                         start, end = c[1]
#                         if start == ord('0') and end == ord('9'):
#                             chars.append("chiffre 0-9")
#                         elif start == ord('A') and end == ord('Z'):
#                             chars.append("lettre majuscule A-Z")
#                         elif start == ord('a') and end == ord('z'):
#                             chars.append("lettre minuscule a-z")
#                         else:
#                             chars.append(f"{chr(start)}-{chr(end)}")
#                     elif c[0] == sre_parse.LITERAL:
#                         chars.append(f"'{chr(c[1])}'")
#                 desc += f"{prefix}- Un des éléments : {', '.join(chars)}\n"
#
#             elif t_type == sre_parse.ANY:
#                 desc += f"{prefix}- N’importe quel caractère\n"
#
#             elif t_type == sre_parse.BRANCH:
#                 desc += f"{prefix}- Alternative (soit … soit …) :\n"
#                 for branch in t_value[1]:
#                     desc += describe(branch, indent + 1)
#
#             else:
#                 desc += f"{prefix}- Token {t_type} : {t_value}\n"
#
#         return desc
#
#     return describe(parsed)