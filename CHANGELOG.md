# Changelog - Totemfall

Todas las adiciones, cambios y correcciones de este proyecto serán documentadas en este archivo.

## [v0.1.0] - Estructura Base y Movimiento del Jugador

### Añadido
- **Entorno Virtual y Framework:** Configuración inicial del proyecto utilizando Pygame y el framework Gale.
- **Máquina de Estados (Game States):** Implementación de la arquitectura de estados principales (`MainMenuState`, `PlayState`, `OptionsState`) para un flujo de juego limpio.
- **Entidad Player Independiente:** Creación de la clase `Player` utilizando su propia máquina de estados (`PlayerIdleState`, `PlayerWalkState`).
- **Sistema de Animación:** Integración de `gale.animation` para reproducir fluidamente los *sprites* del mago (idle y walk) basándose en una cuadrícula exacta de 26x18 píxeles.
- **Renderizado del Nivel:** Implementación de la plataforma de defensa (`sprStairs.png`) en la parte superior del `PlayState`, reservando espacio (HUD) para la futura interfaz.
- **Cursor Táctico:** Se ocultó el cursor nativo de Windows y se reemplazó por un *crosshair* personalizado (`sprCursor.png`) que sigue el mouse en coordenadas virtuales escaladas.
- **Matemática de Disparo (Fundamentos):** Incorporación de la lógica trigonométrica (`math.atan2`) que calcula el ángulo exacto entre el centro del jugador y el cursor del mouse, preparando el terreno para el sistema de *Object Pooling* de proyectiles.

### Cambiado
- **Controles del Sistema:** Se eliminó la salida accidental del juego con `ESC`. Ahora se requiere presionar la combinación `Ctrl + Q` para cerrar la aplicación de forma segura.