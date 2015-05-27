# Script SSH

## Principe

Le script principale est sendtoip.sh qui lit sur son entrée standard la liste des ip à qui envoyer des commandes. La liste doit être sous forme :
2.0.2.XXX\n
2.0.2.YYY\n
2.0.2.ZZZ\n
.....
...
etc

Pour cela on peut soit les envoyer une par une : 
$ cd $path_to_ssh_dir
$ echo 2.0.2.XXX | ./sendtoip.sh
$ echo 2.0.2.YYY | ./sendtoip.sh

Ou par plusieurs :
$ cd $path_to_ssh_dir
$ echo "2.0.2.XXX\
2.0.2.YYY\
2.0.2.ZZZ" | ./sendtoip.sh

Ou toutes les IP de 2.0.2.1/24 avec le script getip.sh :
$ cd $path_to_ssh_dir
$ ./getip.sh | ./sendtoip.sh

On peut aussi envoyer à toutes les ip sauf certaines :
$ cd $path_to_ssh_dir
$ ./getip.sh | grep -v 2.0.2.XXX | grep -v 2.0.2.YYY | ./sendtoip.sh


## Les scripts qui s'éxecutent 

L'executable sendtoip.sh prend au moins un argument, le script à lancer une fois connecté
Par exemple le poweroff :
$ cd $path_to_ssh_dir
$ echo 2.0.2.XXX | ./sendtoip.sh ./poweroff.sh

## Scripts avec arguments

Le script set_branch_and_timeline.sh prendre comme premier argument la branch git à forcer et la timeline à mettre comme ceci :
$ cd $path_to_ssh_dir
$ echo 2.0.2.XXX | ./sendtoip.sh ./set_branch_and_timeline.sh master martigues

## Faire ses scripts

Pour faire soit même un scirpt c'est facile, il suffit de créer un fichier qui contient le scirpt bash et de l'appeler comme les autres scirpts.
Exemple :
$ cd $path_to_ssh_dir
$ nano monscript.sh
\# Ecriture du script 
$ echo 2.0.2.XXX | ./sendtoip.sh ./monscript.sh

Attention : Pas de commetaires dans le script (pas de ligne qui contienne des \# )

Pour récupérer des arguments dans le script il faut utiliser la syntaxe @1 pour le premier agrument (master dans l'exemple de set_branch_and_timeline.sh), @2 pour le second (martigues dans l'exemple de set_branch_and_timeline.sh) etc..

Attention : pas de / dans les arguments (probleme avec sed) donc pas de branches type feature/machine malheureusement



