<table>
<colgroup>
<col style="width: 21%" />
<col style="width: 78%" />
</colgroup>
<tbody>
<tr>
<td rowspan="2"><img src="images/image1.jpeg"
style="width:1.38681in;height:1.47153in"
alt="logo_IGN_pour_lettre" /></td>
<td style="text-align: center;"><p><strong>Manuel utilisateur du plugin
« Jeux d’attributs génériques »</strong></p>
<p><strong>V0.1</strong></p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
</tr>
</tbody>
</table>

<table style="width:100%;">
<colgroup>
<col style="width: 24%" />
<col style="width: 18%" />
<col style="width: 5%" />
<col style="width: 11%" />
<col style="width: 5%" />
<col style="width: 7%" />
<col style="width: 4%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th colspan="4" style="text-align: center;">Identifiant</th>
<th colspan="3" style="text-align: center;">Version</th>
<th style="text-align: center;">Date de création</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="4"></td>
<td colspan="3" style="text-align: center;"><strong>0.1</strong></td>
<td style="text-align: center;">18/11/2025</td>
</tr>
<tr>
<td>Rédacteur</td>
<td colspan="7">Gérôme PECHEUR</td>
</tr>
<tr>
<td><em>Entité émettrice</em></td>
<td colspan="7">DTSO</td>
</tr>
<tr>
<td>Diffusion</td>
<td colspan="2">□ Interne</td>
<td colspan="3">■ Ouverte</td>
<td colspan="2" style="text-align: center;">□ Limitée</td>
</tr>
<tr>
<td>Résumé</td>
<td colspan="7">Installation et utilisation du plugin</td>
</tr>
<tr>
<td>Approbateur</td>
<td></td>
<td colspan="3">Date d’approbation</td>
<td colspan="3" style="text-align: center;">18/11/2025</td>
</tr>
</tbody>
</table>

| Lecteur(s) |     |
|------------|-----|

| Version |    Date    | Modifié par    | Historique des modifications |
|:-------:|:----------:|----------------|------------------------------|
|   0.1   | 18/11/2025 | Gérôme PECHEUR | Création                     |

**Sommaire**

[1 Prérequis](#prérequis)

[2 Résumé](#résumé)

[3 Installation](#installation)

[4 Présentation](#présentation)

[5 Filtrage des champs](#filtrage-des-champs)

[5.1 Sélection unique / multiple](#sélection-unique-multiple)

[5.2 Sélection via <img src="images/image2.png"
style="width:0.23478in;height:0.20798in" />](#sélection-via)

[6 Modification des valeurs des champs](#modification-des-valeurs-des-champs)

[7 Modification de l’ordre d’affichage des « widgets »](#modification-de-lordre-daffichage-des-widgets)

[8 Paramétrage des préférences de l’interface](#paramétrage-des-préférences-de-linterface)

[9 A propos](#a-propos)

# 

# Prérequis

Version de QGIS : 3.28 ou supérieur.

Ce plugin fonctionne en parallèle avec le plugin « maitre ».

# Résumé

Ce plugin est une aide à la modification des attributs des différents
champs.

Un filtre permet de sélectionner uniquement les champs que l’on veut
modifier.

# Installation

Au préalable il faut installer le plugin « Maitre », c’est lui qui gère
l’intégration du plugin dans le menu IGN et / ou dans les barres
d’outils. Sans lui le plugin « jeux d’attributs génériques » ne sera pas
accessible.

Le plugin « espace collaboratif » doit également être installé afin
d’impacter les modifications des couches vers les serveurs IGN, sinon
seules les données locales seront modifiées.

Ouvrir QGIS.

Allez dans **Extensions/Installer/Gérer les extensions**, cliquez sur
**Installer depuis un ZIP**, sélectionner le fichier ZIP puis cliquez
sur **Installer le plugin**.

<img src="images/image3.png"
style="width:6.83889in;height:1.525in" />

# Présentation

<img src="images/image4.png"
style="width:4.27847in;height:0.79097in" />

Lors de la première ouverture de l’interface, seul les boutons par
défauts apparaissent.

En effet le filtrage des champs est pour l’instant vide.

<img src="images/image5.png"
style="width:0.27847in;height:0.27847in" />  Permet de configurer le
filtrage des champs.

<img src="images/image6.png"
style="width:0.26111in;height:0.26944in" /> Permet de paramétrer
l’interface (couleurs, nombre de boutons par ligne)

<img src="images/image7.png"
style="width:0.27847in;height:0.26111in" /> Afficher / Masquer le sens
de numérisation des linéaires

<img src="images/image2.png"
style="width:0.30417in;height:0.26944in" /> Permet de sélectionner
toutes les entités comprises entres deux linéaires en suivant
l’algorithme du « chemin le plus court »

<img src="images/image8.png"
style="width:0.30417in;height:0.27847in" /> Permet d’afficher le suivi
des versions et d’ouvrir la documentation du plugin.

<img src="images/image9.png"
style="width:0.27847in;height:0.27847in" /> Permet d’importer une
configuration des filtres des champs.

<img src="images/image10.png"
style="width:0.29583in;height:0.26944in" /> Permet d’exporter la
configuration des filtres des champs

<img src="images/image11.png"
style="width:1.37391in;height:0.29583in" /> Permet de valider les
modifications dans QGIS. Les modifications vers le serveur IGN seront
effectives uniquement après avoir enregistré les modifications de la
couche via :<img src="images/image12.png"
style="width:0.18261in;height:0.20538in" />

**<span class="mark">ATTENTION</span> :** ne pas confondre avec
l’enregistrement du projet : <img src="images/image13.png"
style="width:0.69565in;height:0.22031in" />

# Filtrage des champs

A la première ouverture le plugin n’affiche aucuns widgets, ceux-ci
doivent être configurés.

- Soit initialement avec un fichier de paramétrage fourni, que l’on peut
  modifier par la suite

- Soit en configurant manuellement les champs à modifier.

Cliquez sur <img src="images/image5.png"
style="width:0.27847in;height:0.27847in" />

<img src="images/image14.png"
style="width:3.14319in;height:3.42609in" />

Cette interface permet de choisir les champs ainsi que les valeurs qui
doivent apparaitre dans l’interface principal pour pouvoir les modifier
par la suite.

En rouge : les champs ne sont pas modifiables, on peut les ajouter juste
pour consultation.

Les champs qui ne peuvent pas se « dérouler » correspondent à des
widgets « zone de texte »

Important : pour les champs « déroulables », ne pas oublier de
sélectionner également une ou plusieurs valeurs.

On actualise l’interface principal avec le bouton « actualiser la
sélection »

## Sélection unique / multiple

Lorsque l’on sélectionne une ou plusieurs entités, l’interface met :

- En vert : les attributs communs à chaque champ pour toutes les entités
  sélectionnées.

- En grisé : les valeurs en lecture seules

- Sans couleur : les valeurs qui ne sont pas communes à toutes les
  entités sélectionnées

> <img src="images/image15.png"
> style="width:4.15924in;height:1.56543in" />

## Sélection via <img src="images/image2.png"
style="width:0.23478in;height:0.20798in" />

<img src="images/image16.png"
style="width:0.25413in;height:0.25413in" /> Ce bouton permet la
sélection de toutes les entités comprises entre 2 linéaires
sélectionnés.

Il faut sélectionner 2 tronçons. Ces 2 tronçons doivent être visibles à
l’écran et être connectés. Ensuite on clique sur
<img src="images/image2.png"
style="width:0.18261in;height:0.16176in" />, le résultat est une
sélection de tous les tronçons entre le premier et le deuxième
sélectionnés respectant l’algorithme du chemin le plus court. Un
contrôle visuel est toutefois nécessaire afin de vérifier si la
sélection faite est celle attendue.

# Modification des valeurs des champs

Une fois les tronçons sélectionnés il suffit de cliquer sur les
nouvelles valeurs choisies.

<img src="images/image17.png"
style="width:4.09565in;height:1.5415in" />

Les valeurs en lecture seules apparaissent en grisé et ne sont pas
modifiables.

Les valeurs à modifier sont affichées sur un fond bleu (par défaut).

Les modifications sur le(s) tronçon(s) sélectionné(s) sont à valider
avec le bouton <img src="images/image11.png"
style="width:1.21048in;height:0.22627in" />

Un message QGIS confirme la prise en compte des modifications.

<img src="images/image19.png"
style="width:4.72917in;height:0.35417in" />

# Modification de l’ordre d’affichage des « widgets »

Apres filtrage des champs-valeurs il peut être pertinent de modifier
l’ordre d’affichage des différents « widgets » dans l’interface
principale.

Cela permet de gérer l’affichage des « widgets » en fonction des plus
utilisées.

Exemple :

Par défaut les « widgets » sont insérés par ordre d’affichage dans le
filtre.

On peut se retrouver avec un widget qui sera souvent utilisé mais qui
sera inséré dans la « combobox » ou dans un bouton mais pas à la
position voulue.

Solution :

Faire un clic-droit sur un « bouton » ou sur une valeur dans le
« combobox »

<img src="images/image20.png"
style="width:1.77373in;height:0.88687in" />

Renseigner la nouvelle position.

L’interface est mise à jour avec la nouvelle position du « widget ».

# Paramétrage des préférences de l’interface

<img src="images/image6.png"
style="width:0.26111in;height:0.26944in" /> Ouvre l’interface de
paramétrage.

<img src="images/image21.png"
style="width:2.76904in;height:1.39136in" />

- Cette interface permet de configurer le nombre de « widgets » par
  ligne

Exemple : ici nous avons 3 « widgets » par ligne, cela signifie que si
on a sélectionné 5 valeurs différentes pour un champ (dans le filtrage),
dans l’interface principale nous auront les 3 premières valeurs sous
forme de « boutons » et les suivantes seront incluses dans une
« combobox » déroulante.

- On peut également modifier les couleurs des différents « widgets »

# A propos

Accessible via <img src="images/image22.PNG"
style="width:0.23962in;height:0.25003in" />.

<img src="images/image23.png"
style="width:3.57157in;height:2.45199in" />

Ce dialogue <img src="images/image6.png"
style="width:0.26111in;height:0.26944in" />permet de suivre l’historique
des différentes versions ainsi que d’afficher cette documentation.
