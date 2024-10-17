Il s'agit d'un simple code shellcode pour un fichier infecté, j'ai créé un programme en langage c hello.c qui sert à produire un hello qui sera utilisé comme fichier infecté.
En lisant les informations ELF du fichier hello, j'ai obtenu les adresses virtuelles du segment LOAD et du segment NOTE.
Écriture d'un simple shellcode qui saute du segment de note au segment de chargement exécutable en insérant une chaîne de caractères « infected » à la fin du segment de chargement.
Utilisez ensuite la commande grep pour vérifier que l'insertion a réussi
Les résultats sont présentés ci-dessous
![a6efdb27e38d8cba041f6d91abc8269](https://github.com/user-attachments/assets/7557453f-0e47-45ea-a036-ed9725cb0210)


