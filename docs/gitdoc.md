# GIT HELP DOC

## Infos générales

git sépare bien deux environnement : *le dossier local* et *les dossiers distants*. Le plus souvent il n'y a qu'un dossier distant, et c'est le cas ici, qui est le dossier git présent sur les serveur de github. Ce dossier distant est appelé **origin** par défaut et c'est le cas ici. Le dossier local n'a pas de nom et c'est ainsi qu'on le reconnait. 
Par exemple, origin/master fait référence à la branch master sur le serveur de github alors que master fait référence à la branch master du dossier local.

## Branch, commit, HEAD

### Commit 

Un commit est un ensemble de modification faites sur des fichiers d'un répertoir git. Il comporte toujours un message de commit ainsi qu'un identifiant unique. En gros un commit est un fichier qui répertorie toutes les différences entre l'état **n** d'une *branche* et l'état **n+1** avec un *court* message qui explique de façon claire ce qu'impliquent les modifications et un uid. Un commit est toujours attaché à une branche. (commande : $ git commit -m "Message" )

### Branch

Une branche est une copie d'un repertoire qui permet d'être hermetique au commits ayant lieux sur les autres branche. Pour créer une branche on duplique une précédente (commande : $ git checkout -b new_branch) en lui changeant juste son nom. Ensuite lorsque l'on fait des modifications et qu'on les commits cela ne se répecrute que sur cette branche. Merge une branche revient à appliquer l'ensemble des commits non présent sur la branche selectionnée depuis la branche choisie. On merge donc une branche XXX vers la branche courante. (commande : $ git merge XXXX)

### HEAD

HEAD est le pointeur courrant de la branche. En quelque sorte cela représente quel est le dernier commit pris en compte par la branche. On peut voir ce commit en faisant appel au log(commande : $ git log -1 ).
On peut déplacer ce pointeur pour revenir en arrière par exemple avec le reset (commande : $ git reset --hard HEAD), qui ici supprime toutes les modifications non sauvegardées depuis le dernier commit.

## Commandes utiles 

$ git status 
Donne quelques infos sur l'état courant du répertoir git, notamment :
 - la branche en cours
 - les fichiers modifiés / suivits / non suivits / les conflits etc..
 
$ git branch
Donne des infos sur l'ensemble des branches locales

$ git log 
Prompt l'ensemble des commit appliqués sur la branche en partant du dernier (donc de HEAD)

$ git tag -a v1.1 -m "Version 1.1 : 30 avril 2015"
Créer un tag sur le commit suivit par HEAD avec un numéro de version (ici v1.1) et un message (ici : Version 1.1 : 30 avril 2015)
Doc : http://git-scm.com/book/en/v2/Git-Basics-Tagging
/!\ Push ne transfert pas les tags si on ne lui dit pas : pour cela : (commande : $ git push origin v1.1)


## Procédures 

### HOTFIX
Pour faire un hotfix sur master suivre cette procedure :
1: Créer un branche temporaire pour le hotfix 
$ git checkout master			# On passe sur master
$ git pull 				# On s'assure d'être à jour sur master
$ git checkout -b hotfix/problem	# On créer une branche temporaire (remplacer problem par quelque qui explicite le problème à régler

2: Faire ses modifications de hot fix et bien les tester 
.. Modifications ..
$ git commit -a -m "Règle tel problème"
.. Test ..
$ git commit -a -m "Règle tel autre problème lié"
.. Test ..
.. Validé ! ..
$ git push -u origin hotfix/problem 	# -u créer la branche distante et la lie avec la branch locale

3: Merger sur master tager et pusher
$ git checkout master
$ git merge hotfix/problem
.. Test ..
$ git tag -a vX.Y-Z+1 -m "Version X.Y-Z+1 du 30 avril 2015 : hotfix de tel problème" 	# Tag la version en ajoutant un au chiffre de hotfix de la version (par convention après le - )
$ git push origin vX.Y-Z+1

4: Retour sur develop et répercution des modifications
$ git checkout develop
$ git merge master
$ git push

### Créer une nouvelle version sur master
Procédure pour la création d'une nouvelle version stable sur master dans le but d'être utilisée sur les RPI en production :
1 : Passage sur master et préparation du terrain
$ git checkout master			# Passage sur master
$ git pull 				# On s'assure d'être à jour
$ git fetch --all			# On s'assure d'être à jour sur toutes les branches

2 : Récupération des modifications sur **la branche distante de develop** (Bien penser à puller ses modifications locales avant)
$ git merge origin develop		# Merge de la branche distante develop vers master
$ git push

3 : Tag et envoie sur le serveur de la nouvelle version 
$ git tag -a vX.Y -m "Version X.Y du 30 avril 2015 : détail de la version"
$ git push origin vX.Y

4 : Retour sur develop
$ git checkout develop

### Créer une branche pour bosser sur une modification en solo
Procédure pour créer une branch solo pour réaliser une fonctionnalité et ne pas 'casser' develop avec des essais 
1 : Création de la branche depuis develop
$ git checkout develop 				# On s'assure d'être sur develop
$ git pull					# On s'assure d'être à jour
$ git checkout feature/mafonction		# Création de la branche pour la création de mafonction
$ git push -u origin feature/mafonction		# Envoie de la branche pour l'instant vide vers le serveur

2 : Modifications et tests
.. Modifications ..
.. Tests ..
$ git commit -a -m "Message de commit"
.. etc ..

(3 optionelle et répétable) : Besoin de push pour partager ses modifications
$ git push 

4 : Fin des modification et merge de master vers la fonctionnalité pour ratraper son retard
$ git fetch --all 				# On récupère tout pour être sur d'être à jour
$ git merge origin develop			# On merge la branche distant de develop
.. Résolution des éventuels confilts et tests ..
$ git push

5 : Publication des modification sur develop après s'être assuré que tout marche bien
$ git checkout develop
$ git pull 
$ git merge feature/mafonction
.. Il ne devrait plus y avoir de conflit mais si jamais on les résouts ..
$ git -a --allow-empty -m "Merge feature/mafonction vers develop"	# Petit commit pour marquer le coup
$ git push





