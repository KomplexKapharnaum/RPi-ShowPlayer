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
