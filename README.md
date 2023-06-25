##Trabajo_Fin_Grado
Código para la integración, procesamiento de datos y creación de análisis univariantes, bivariantes y de supervivencia
# Herramientas de Análisis de Datos Médicos

Este repositorio contiene un conjunto de herramientas y scripts desarrollados en Python para el análisis de datos médicos. Estas herramientas permiten la integración y procesamiento de datos, la creación de gráficas informativas y la generación de diapositivas en PowerPoint para presentación de resultados.

## Estructura del Repositorio

El repositorio está organizado en tres carpetas principales:

1. `integracion_procesamiento`: Esta carpeta contiene los scripts y módulos auxiliares necesarios para la integración y procesamiento de los datos médicos. Los archivos incluidos son:
    - `concat.py`: Realiza la integración de tablas obtenidas de una base de datos relacional en un único DataFrame de pandas.
    - `procesamiento.py`: Realiza el procesamiento de variables médicas de interés para su posterior análisis.

2. `creacion_diapositivas`: En esta carpeta se encuentran las funciones y código necesarios para la generación de diapositivas en PowerPoint. Los archivos incluidos son:
    - `univ_funciones.py`: Contiene funciones para la creación de gráficas de distintos tipos de variables, el manejo de valores faltantes y errores en la recopilación de datos, y la generación de diapositivas informativas en PowerPoint.
    - `biv_funciones.py`: Similar a `univ_funciones.py`, pero incluye funciones para el análisis bivariante de datos, tomando una variable agrupadora como argumento.

3. `analisis_de_datos`: Esta carpeta contiene los scripts principales para la realización de análisis de datos. Los archivos incluidos son:
    - `Univ_main.py`: Genera análisis univariantes y crea diapositivas en PowerPoint.
    - `Biv_main.py`: Genera análisis bivariantes y crea diapositivas en PowerPoint.
    - `surv_main.py`: Proporciona una interfaz gráfica para generar curvas de supervivencia y descargar los resultados en formato PowerPoint.


Para ejecutar los scripts principales, simplemente abre una terminal en el directorio correspondiente y ejecuta el comando `python <nombre_del_script>.py`. 
