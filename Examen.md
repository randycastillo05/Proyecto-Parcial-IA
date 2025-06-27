# Examen Parcial

**Valor:** 20 puntos

**Fecha de entrega:** 07/07/2025

**Fecha de presentación:** 10/07/2025 y 12/07/2025

---

## Desarrollar un juego utilizando Pygame

El proyecto final consiste en realizar un _fork_ del repositorio de GitHub donde se encuentra este archivo y, a partir de él, desarrollar un juego en el que el jugador debe interactuar con uno o más agentes en un entorno competitivo hasta ganar o perder. El juego debe incluir al menos un **Árbol de Comportamiento** y un algoritmo **A\***.

### Detalles:

- El juego puede ser un clon de algún juego existente, pero debe programarlo usted mismo.
  Si utiliza un proyecto de Internet y lo hace pasar como suyo, **reprobará el parcial**.

- Deberá presentar el juego a personas que lo probarán frente a usted. Además, deberá explicar cómo funciona su proyecto y cómo está implementada la inteligencia artificial en él.

- También deberá subir un video de su juego explicando cómo lo desarrolló, el funcionamiento de los algoritmos en profundidad y mostrando cómo se juega.

  - El video debe estar en formato **MP4**.
  - Evite subir videos de **15 minutos que pesen 4 GB**.
  - En el video debe aparecer usted en cámara explicando su proyecto mientras muestra el código y el juego en funcionamiento.
  - La relación del video debe ser **16:9** y la resolución mínima debe ser **720p**.

- Si un trabajo presenta **solo** el Árbol de Comportamiento o **solo** el A\*, se restarán **10 puntos** de la calificación.
  Si no incluye ninguno de los dos, el proyecto valdrá **0**.

- La estructura del proyecto debe ser la siguiente:

```Plaintext
proyecto/
│── main.py
├── scripts/
│   ├── ...
│   ├── ...
├── assets/
│   ├── images/
│   ├── sounds/
│   ├── music/
├── requirements.txt
└── README.md
```

Más lo que ya incluía el repositorio original.

- El Árbol de Comportamiento, el algoritmo A\*, y en general toda la lógica de los agentes, debe estar implementada **desde cero**.
  No se debe utilizar ninguna librería externa para esto.
  **No se recibirán proyectos que incumplan este punto.**

- El juego debe incluir el uso de **controles / gamepad**. Este punto es **obligatorio**.

- El juego debe incluir **sonidos y música**.
  Pueden ser descargados de Internet o generados por usted.

- El juego debe incluir **sprites**, que pueden ser descargados de Internet, tomados de juegos famosos, hechos por usted o generados con inteligencia artificial.

- El juego debe contar con un **menú** que permita:

  - **Iniciar el juego**
  - **Reiniciar la partida** al terminar o perder

- El **rendimiento del juego será evaluado**.
  Si el rendimiento es deficiente, se aplicarán penalizaciones.

- Su juego debe estar en un repositorio de **GitHub** y debe contar con el historial de _commits_ correspondiente al proyecto.

  - Se evaluará el historial en caso de encontrar irregularidades.
  - Se recomienda hacer _commits_ con cada funcionalidad y cambio, con mensajes descriptivos.

  - Utilizar git para el proyecto es obligatorio, si sube archivos manualmente al repositorio no se va a evaluar su proyecto y la calificación será **0**.

- **Los proyectos son individuales y no pueden repetirse.**
  - Hay un foro en la carpeta de exámenes donde debe indicar qué juego desarrollará.
  - Así quedará constancia de que alguien eligió su proyecto primero.
  - Si está haciendo un clon de un juego existente, deje un **enlace a un video en YouTube** del juego junto con su descripción.

### Formato de entrega:

- El proyecto debe subirse en un **archivo ZIP** a la plataforma que incluya:

  - Un **archivo de texto plano** con su **nombre, matrícula y el enlace al repositorio de GitHub**.
  - El **video con las explicaciones**.

- El **nombre del archivo ZIP** debe ser su **nombre y matrícula**.

### Estructura del repositorio:

- Debe contener los scripts de Python, imágenes, sonidos o cualquier recurso necesario para ejecutar el proyecto.
- Debe incluir un archivo `requirements.txt` con las librerías utilizadas.

  - Este archivo permite instalar todas las dependencias con un solo comando.
  - **Si no sabe qué es `requirements.txt`, investigue.**
    No envíe un PDF con las librerías, ni un archivo que diga "las librerías usadas son:".
    **Por el amor de Dios, investigue.**

- Utilice un archivo `.gitignore` para evitar subir binarios y archivos innecesarios que aumenten el tamaño del repositorio.

### Código y comentarios:

- Los scripts de Python deben contener **comentarios** que faciliten la lectura del código.
- Cada script debe incluir un **comentario con su nombre y matrícula**.

---

**El proyecto debe subirse a la carpeta de _Examen Parcial_ hasta el 07/07/2025.**
**Pasada esa fecha no se recibirán proyectos.**
