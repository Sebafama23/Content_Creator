GUIA PASO A PASO PARA TENER TU CONTENT CREATOR TRABAJANDO EN DOCKER DE FORMA LOCAL.

1- Abrir Docker: 
Paso manual.

2- Buildear imagen: 
#docker build -t content_creator_image .

3- Montar conteiner: 
#docker run -d --name Content_creator -v C:\Docker-teiners\Content_Creator:/app content_creator_image

4- Correr los scripts:
a) 
#docker exec -it Content_creator python src/1-researcher.py
b) 
#docker exec -it Content_creator python src/2-generator.py
c)
#docker exec -it Content_creator python src/3-publisher.py
