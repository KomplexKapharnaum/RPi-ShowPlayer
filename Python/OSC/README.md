# README : OSC
 
## ACK OSC
 
 **Principe** : Pouvoir être sûr qu'un message est arrivé a destination.
 
 **Mise en place** : Envoie d'un message avec en tête. Il faut renvoyer l'entête à l'emetteur pour lui signifier que l'on a bien reçu l'information
 
 **Détails** : L'entête comprends les informations suivantes :
  
  - BOOLEAN (T/F) : T = SYN // F = ACK (SYN pour l'envoie du message, ACK pour confirmer la reception)
  - INTEGER (i) : Sur 4 bytes un bout de time stamp
  - INTEGER (i) : Sur les 2 premiers bytes un random qui vient s'ajouter au timestamp pour l'aléatoire. Sur les deux bytes d'apres le numéro de port pour pouvoir répondre
  
 
 


