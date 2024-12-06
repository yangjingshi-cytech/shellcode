Aperçu du projet

En exploitant le segment PT_NOTE du fichier ELF, il le modifie en PT_LOAD et ajoute le code du virus à la fin du fichier. 

Il a la capacité d'afficher un message spécifique lors de sa première exécution et tentera d'infecter d'autres fichiers dans le répertoire actuel après l'infection

Le caractère « infecté par yangjing » s'affiche après une infection réussie.

![image](https://github.com/user-attachments/assets/9143eb4a-a63e-4e9a-bb83-e9a5c2d58b89)

Lorsque le programme infecté est exécuté à nouveau, il émet le caractère <hello!its me!>

1)Exploit the vulnerability

La section PT_NOTE du fichier ELF a été utilisée pour transformer la section de commentaires en section exécutable en la remplaçant par PT_LOAD.

2)Infect a file to achieve persistence through the previously done infector

Infecte les fichiers ELF en modifiant la table des segments et l'adresse d'entrée du fichier, en ajoutant le code du virus à la fin du fichier, ce qui garantit que le code du virus est exécuté à chaque fois que le fichier est exécuté.

3)Continue the pwned process without crashing

Après l'infection, il reprend l'exécution du programme original, en revenant au point d'entrée du programme original via l'instruction de saut

4)Verify the infected binary can be launched

Avant:

ADD:

![image](https://github.com/user-attachments/assets/365771f2-fc4f-44ff-8074-c5d77335ec53)

HELLO:

![image](https://github.com/user-attachments/assets/e510488a-3162-40a0-aa08-308b74dfcc17)

Apres:

ADD：

![image](https://github.com/user-attachments/assets/7105f582-3afb-498a-93ca-0dd37e8e712c)

HELLO:

![image](https://github.com/user-attachments/assets/40fff442-713e-40cd-a230-d7883483285d)

5)Search for techniques that are reliable across hosts

utilise le format de fichier ELF commun et utilise des appels système standard dans l'environnement Linux, de sorte qu'il peut également être exécuté sous d'autres hôtes.





