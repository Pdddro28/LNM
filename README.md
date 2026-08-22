**If you want to see this repository in English, [click here](https://github.com/Pdddro28/K-O-M-R-A-D/blob/main/README_EN.md)**

``` Para mejor visualización, se recomienda ver el repositorio en la computadora ```

# WRO 2026 Future Engineers – LNM

<div align="center">
	
<img width="840" height="407" alt="WhatsApp Image 2026-06-19 at 11 51 57 PM" src="https://github.com/user-attachments/assets/cee364df-eeba-4338-8f2a-14949adb755b" />

</div>

Bienvenidos al repositorio de GitHub del **Equipo LNM**, anteriormente conocido como Ars Machina, que compite en la categoría **World Robot Olympiad™ (WRO®) Future Engineers 2026**. Nuestro equipo está formado por David Wang y Pedro Catamo que han diseñado un vehículo autónomo compacto e innovador para hacer frente a los retos dinámicos de la competición WRO 2026.

## **Índice**

**1. [Estructura de carpetas](#estructura-de-carpetas)**

**2. [El equipo](#el-equipo)**

**3. [Nuestro robot](#nuestro-robot)**

**4. [Sistemas electrónicos](#sistemas-electronicos)**

**5. [Sistemas mecánicos](#sistemas-mecanicos)**

**5. [Arquitectura de software](#arquitectura-de-software)**

---

## **Estructura de carpetas** <a id="estructura-de-carpetas"></a>

Esta es la estructura de carpetas de nuestro repositorio:
<div align="center">
	
| Carpeta | Contenido técnico | Documentación detallada |
|---|---|---|
| **models** | **Diseños 3D**<br>• Piezas del carro| [Explora los modelos 3D](models/README.md) |
| **schemes** | **Sistemas eléctricos**<br>• Diagramas de cableado<br>• Gestión de la alimentación<br>• Esquemas de componentes| [Explora la documentación de esquemas y cableado](schemes/README.md) |
| **src** | **Algoritmos de software**<br>• Lógica de navegación<br>• Fusión de sensores<br>• Sistemas de control | [Explora la documentación de software y algoritmos](src/README.md) |
| **t-photos** | **Documentación del equipo**<br>• Perfiles de los miembros | [Explora la documentación de fotos del equipo](t-photos/README.md) |
| **v-photos** | **Documentación del vehículo**<br>• Vistas desde múltiples ángulos | [Explora la documentación de fotos del vehículo](v-photos/README.md) |
| **video** | **Validación del rendimiento**<br>• Demostraciones del desafío<br>• Pruebas de ingeniería | [Explora la documentación de los vídeos de rendimiento](video/README.md) |

</div>

---

## **El Equipo** <a id="el-equipo"></a>

<div align="center">
	
<img width="1280" height="720" alt="Team_pic (1)" src="https://github.com/user-attachments/assets/156c3c29-799e-44e6-a7f0-629da61873b8" />

</div>

### **Miembros:**
<div align="center">

| **Miembro** | **Miembro** | **Coach** |
| :---: | :---: | :---: |
| 👤 **David Wang** | 👤 **Pedro Catamo** | 👤 **Jesús Alcalá** |
| 📅 **Nacido en:** 01/04/2011 (15 años)<br>🏫 **Estudio:** 4º año en la U.E.C. Eduardo Blanco<br>📧 **Gmail:** [davidwangwu104@gmail.com](mailto:davidwangwu104@gmail.com) | 📅 **Nacido en:** 28/01/2009 (17 años)<br>🏫 **Estudio:** 5º año en la U.E.C. Eduardo Blanco<br>📧 **Gmail:** [pedrocatamo.2009@gmail.com](mailto:pedrocatamo.2009@gmail.com) | 📅 **Nacido en:** 18/11/2005 (21 años) <br> 🏫 **Estudio:** Ingenieria en computación & Ingenieria informática <br> 📧 **Gmail:** [Jdam50002@gmail.com](mailto:Jdam50002@gmail.com) |

</div>

---

### Diseños anteriores:
  
<div align="center">
	
| Foto | Nombre | Descripción |
|---|---|---|
| <img width="920" height="920" alt="Captura de pantalla 2026-06-17 185504" src="https://github.com/user-attachments/assets/36166165-a542-42d6-a771-41a60693a399" /> | **Cyber Cooper** | En 2023 teníamos pensado diseñar el coche desde cero, modelando e imprimiendo nuestras propias piezas en 3D, incluidos el chasis y el sistema de dirección. Aunque al principio parecía una buena idea, a medida que avanzábamos empezamos a encontrarnos con un problema tras otro, y nos dimos cuenta de que nuestro diseño actual nos acarrearía más dificultades. Al final, hicimos todo lo que pudimos dentro de las limitaciones de tiempo que teníamos. |
| <img width="920" height="920" alt="front2" src="https://github.com/user-attachments/assets/ce130237-cc0b-4aa9-a620-0aea287408c2" /> | **Cooper** | En 2024 desarrollamos un chasis con piezas 3D estructurado en dos niveles. El nivel inferior albergaba los sensores y la electrónica de bajo nivel, mientras que el superior sostenía las baterías y la Raspberry Pi 3 para optimizar el espacio. Aunque logramos un gran avance estético y funcional, sufrimos lecciones duras en pista: el peso excesivo provocó la flexión de los acoples en la transmisión trasera, lo cual, a su vez, generó problemas severos de fricción mecánica entre las piezas impresas en 3D. |
| <img width="920" height="920" alt="front" src="https://github.com/user-attachments/assets/804b3d7f-3500-4351-a917-ccf781029804" /> | **Halbi** | En 2025 teniendo en cuenta los recursos de los que disponíamos en ese momento, nuestra idea principal era rediseñar el Cybercooper, modificando la base y la estrategia existentes y utilizando mejores componentes electrónicos; empezamos a imprimir las nuevas piezas con material blanco y a pensar en mejores formas de montar el sistema de dirección del coche. Al final, decidimos utilizar una base prefabricada para el chasis; la razón principal fue ahorrar tiempo (y dolores de cabeza) con el diseño mecánico, lo que nos permitía dedicar más tiempo a la electrónica y la programación. |
| <img width="920" height="920" alt="WhatsApp Image 2026-06-18 at 7 39 40 PM" src="https://github.com/user-attachments/assets/ca9f62ff-7b8b-452a-97de-95ebf12dc0ef" /> | **The Fridge** | En 2025 a diferencia de los modelos anteriores que pertenecían a nuestro coach, "The Fridge" fue un diseño construido enteramente por nosotros. Aquí dimos el salto a la geometría Ackermann e imprimimos la gran mayoría de las piezas en 3D. A nivel motriz, usamos un motor DC con un engranaje acoplado para traccionar ambas ruedas. Físicamente le instalamos 3 sensores ultrasónicos, una Raspberry Pi 4 y un giroscopio MPU6050, pero por falta de tiempo y severos problemas de configuración, la Raspberry y el IMU quedaron como peso muerto y terminamos controlando todo únicamente desde la MegaPi. Sufrimos muchísimo: las piezas de la dirección impresas en 3D se rompían constantemente por el estrés, y programar la navegación autónoma en Arduino dependiendo de puros rebotes ultrasónicos fue casi imposible. Siendo sinceros, terminó siendo el peor proyecto de los tres. |

</div>

---

# 1- Mobilidad y diseño

 - ### Halbi The Green: <a id="nuestro-robot"></a>

    - ### Fotos del vehiculo:

	<div align="center">

	| | **Diferentes ángulos del carro** | |
	|---|---|---|
	| **Superior** | **Derecha** | **Izquierda** |
	| <img width="560" height="580" alt="Upper-Pov" src="https://github.com/user-attachments/assets/74863cc8-5128-49cf-845e-0f087c50bcf1" /> | <img width="560" height="580" alt="RightSide-Pov" src="https://github.com/user-attachments/assets/8b9c2020-cc18-441f-9152-c86d9a233b10" /> | <img width="560" height="580" alt="LeftSide-Pov" src="https://github.com/user-attachments/assets/cdbabe27-6e45-4dab-98e6-e63b24ed7371" /> |
	|**Frontal** | **Trasero** | **Libre** |
	| <img width="560" height="580" alt="Front-Pov" src="https://github.com/user-attachments/assets/d9b65dd5-ca97-4087-ba20-77f7cbeb4bf6" /> | <img width="560" height="580" alt="Back-Pov" src="https://github.com/user-attachments/assets/dd1737be-1173-4cae-9229-25821f05dc22" /> | <img width="560" height="580" alt="604003001-cc130bf0-8547-48cc-847e-28dbd9029fba" src="https://github.com/user-attachments/assets/f1dc12a1-dbfc-46f3-9a21-a679aa1aa3db" /> |
	
    </div>

	- ### Especificaciones mecánicas principales: <a id="sistemas-mecanicos"></a>

		- **Dimensiones totales: 24.4 cm (largo) × 15.4 cm (ancho) × 15.9 cm (alto).**
		- **Peso del carro: aproximadamente 1.2kg.**
		- **Sistema de tracción: Tracción Trasera Mecánica Bifásica.**
		- **Sistema de dirección: Geometría Ackermann.**
	
	- ### Mecanismo de Dirección Ackermann

		El vehículo utiliza una geometría precisa basada en el **Principio de Dirección Ackermann** para conquistar curvas cerradas con cero deslizamiento lateral y un desgaste mínimo de los neumáticos.

		* **La Física Detrás del Principio:** Cuando un vehículo entra en una curva, la rueda delantera interior sigue un radio concéntrico más cerrado y pequeño que la rueda exterior. Si ambas ruedas giraran exactamente al mismo ángulo, los neumáticos lucharían entre sí, provocando que el neumático exterior se arrastre, pierda agarre mecánico e introduzca vibraciones estructurales severas que arruinarían el seguimiento visual de los carriles. Para resolver esto, la geometría mecánica obliga a la rueda interior a pivotar a un ángulo más profundo que la rueda exterior, asegurando que las cuatro ruedas roten alrededor de un único centro instantáneo de curvatura (ICC) común.

		* **La Ejecución Mecánica:** Un servo digital **MG996R** de alto par ($11 \text{ kg}\cdot\text{cm}$ de par) se ancla al mamparo delantero mediante un soporte de aluminio en forma de L mecanizado a medida para eliminar la deflexión estructural. El brazo del servo acciona una cremallera de dirección de doble enlace conectada a tirantes asimétricos y manguetas de dirección. Los brazos de dirección están angulados hacia el interior, apuntando al centro del eje trasero, completando el clásico "Trapezoide de Ackermann". Este diseño mecánico exacto convierte el desplazamiento lineal del servo en ángulos de rueda no lineales de forma automática.

		* **El Control Digital y Calibración:** El MG996R es controlado por un tren de pulsos PWM por hardware continuo y libre de fluctuaciones (*jitter*) a $50\text{Hz}$ directamente desde el microcontrolador MegaPi. La dirección está rígidamente mapeada y calibrada a una banda muerta de software donde los $80^\circ$ representan el centro geométrico absoluto. Los puntos finales mecánicos están limitados por software entre $40^\circ$ (Máximo Izquierda) y $105^\circ$ (Máximo Derecha) para evitar que los eslabones de la dirección alcancen un bloqueo mecánico o fuercen los límites de pérdida del motor.

	<div align="center">

	Imagen

	</div>

	- ### ¿Qué es la Geometría Ackermann? 

		Entendiendo la Matemática y Cinemática Ackermann, en robótica móvil tradicional (como los robots de la categoría *RoboMission*), se utiliza la tracción diferencial porque es matemáticamente simple: varías la velocidad de dos motores y el robot gira sobre su propio eje. Sin embargo, a altas velocidades, la tracción diferencial es inestable e impredecible.

		**La Geometría Ackermann** resuelve esto mediante un principio puramente mecánico. Para que un vehículo gire sin deslizarse lateralmente, las líneas extendidas desde los ejes de todas las ruedas deben cruzarse en un único punto en el espacio: el **Centro Instantáneo de Rotación (CIR)** o ICC.

		La ecuación matemática fundamental que gobierna esta cinemática es:
		<div align="center">
	
		$$\cot(\theta_{\text{out}}) - \cot(\theta_{\text{in}}) = \frac{w}{L}$$
		
		</div>
		
		Donde:
		
		* $\theta_{\text{in}}$ es el ángulo de giro de la rueda interna.*
		* $\theta_{\text{out}}$ es el ángulo de giro de la rueda externa.*
		* $w$ es el ancho de la vía (*track width* o distancia entre las ruedas frontales).*
		* $L$ es la batalla del carro (*wheelbase* o distancia entre el eje delantero y trasero).*

		Dado que la cotangente crece más rápido a ángulos pequeños, esta relación obliga mecánicamente a que $\theta_{\text{in}} > \theta_{\text{out}}$ de forma automática en cualquier curva, abriendo el ángulo de la rueda exterior para que dibuje un círculo más grande.

		<div align="center">
  
		<img width="567" height="600" alt="17523247_203569336801744_2788986523412924047_n" src="https://github.com/user-attachments/assets/c36a271c-b45c-492a-805e-b107851429cd" />
		
		</div>

	- ### Propulsión Electrónica 2WD con Transmisión Mecánica Bifásica 

		La fuerza motriz de la plataforma se genera mediante un sistema de tracción trasera (2WD) de alto rendimiento, el cual rompe con los esquemas tradicionales de acoplamiento directo al integrar una transmisión mecánica desmultiplicada de dos velocidades por engranajes cilíndricos rectos.

		* **Arquitectura del Sistema de Transmisión:** A diferencia de las configuraciones comunes que acoplan la rueda directamente a la caja reductora del motor, este diseño monta el motor RS380 en una disposición paralela superior sobre un bloque de soporte rígido. La potencia se transfiere desde el eje primario del motor hacia un eje secundario de tracción inferior mediante un tren de engranajes expuesto con dentado recto. Este sistema de dos velocidades mecánicas intercambiables permite configurar el robot según las exigencias de la pista:
  		1. **Relación de Fuerza/Torque (Primera Velocidad):** Optimiza el desmultiplique para obtener la máxima aceleración y un control milimétrico en curvas cerradas u obstáculos, ideal para tramos revirados. 
  		2. **Relación de Velocidad Final (Segunda Velocidad):** Reduce la pérdida de revoluciones para aprovechar la inercia lineal en rectas largas, garantizando una alta velocidad de crucero sin saturar el consumo eléctrico.

		<div align="center">
  
		<img width="515" height="218" alt="Sistema de transmision de 2 velocidades K-O-M-R-A-D" src="https://github.com/user-attachments/assets/da8175e6-313d-42d6-bd3b-b1318082536f" />
		
		</div>

		* **Especificaciones Técnicas de los Motores (RS380):** El bloque motriz confía en motores de CC con escobillas imantadas, seleccionados específicamente por su curva de respuesta dinámica y tolerancia a picos transitorios de carga.

	    * **Voltaje Nominal:** $12\text{V}$ (Operando a un voltaje nominal de celda de $11.1\text{V}$ mediante una batería LiPo 3S para asegurar la estabilidad térmica).
   
 		* **Corriente de Vacío (No-load):** $0.3\text{A}$ | **Corriente de Arranque/Pérdida (Stall):** $3\text{A}$ de protección en el driver.
   
 		* **Velocidad de Rotación de Fábrica:** $15000\text{ RPM}$ en el núcleo del motor, reducida internamente y ajustada finalmente por el engranaje externo para entregar una velocidad final estimada de transferencia de aprox. $450\text{ RPM}$ en el eje de la rueda.

		* **Análisis Cinemático y Cálculo de la Velocidad Teórica Absoluta:**
		Para determinar el rendimiento del chasis en pista y calibrar las ventanas de tiempo por vuelta (como el parámetro de control `lap_time = 4.3`), se realiza el cálculo cinemático basado en el diámetro de las ruedas motrices de $6.5\text{ cm}$ ($0.065\text{ m}$). Evaluamos la circunferencia de rodadura ($C$) y la velocidad lineal máxima teórica ($V$):

	<div align="center">
	
	$$C = \pi \times 0.065\text{ m} \approx 0.2041\text{ m}$$

	</div>

	Transformando las revoluciones por minuto del eje secundario de la transmisión a revoluciones por segundo y multiplicando por el desarrollo de la circunferencia, obtenemos la velocidad de avance del chasis:

	<div align="center">
	
	$$V = \frac{450\text{ RPM}}{60} \times 0.2041\text{ m} \approx 1.53\text{ m/s}$$
		
	</div>

	Este valor de $1.53\text{ m/s}$ representa la velocidad límite ideal de la plataforma. En condiciones reales de competencia, este vector se modula por software mediante los comandos de velocidad (`speed = 90` u `80`) para absorber la fricción estática del suelo, la resistencia al avance de los rodamientos y las demandas instantáneas de corriente solicitadas por la MegaPi al gestionar el cambio de inercias.


	- ### 3D Printed Parts:

   		- #### **Piezas:**

		<div align="center">
			
		| Component & Preview | Design & Geometry | Engineering Purpose |
		|---|---|---|
		| **Battery Case** <br><br><img width="400" height="400" alt="BatteryCase" src="https://github.com/user-attachments/assets/a5362844-dd0e-4073-bef8-bb034bae3ad9" /> | Diseñado como una jaula de torre vertical estructurada con cuatro pilares reforzados en cada lado, integrada directamente sobre una base de montaje sólida con ojales para tornillos en las esquinas. Las paredes laterales cuentan con grandes recortes circulares para minimizar el peso del material mientras permiten un flujo de aire pasivo máximo para evitar el estrés térmico en las celdas LiPo durante altas tasas de descarga. El pilar superior incluye ojales de retención ranurados para una sujeción segura de las correas. | Centraliza la masa combinada de las celdas de la batería verticalmente a lo largo del eje geométrico central del chasis. Este diseño de jaula abierta garantiza un acceso rápido para el reemplazo de la batería entre carreras, al tiempo que proporciona una contención estructural rígida contra las fuerzas de inercia laterales durante giros a alta velocidad. |
		| **Camera Case** <br><br><img width="400" height="400" alt="CameraCase" src="https://github.com/user-attachments/assets/7adbc42b-15eb-4677-a0a4-8d9b3c98bab3" /> | Una carcasa protectora rectangular y compacta, diseñada específicamente para encapsular el sensor IMX219 (Arducam). La sección inferior integra una robusta bisagra de pivote cilíndrico que cuenta con dientes de bloqueo externos (perfil de engranaje recto) diseñada para engranar perfectamente con una base de montaje correspondiente para el bloqueo mecánico del ángulo. | Protege el delicado PCB de la cámara de los escombros externos o de los impactos directos en la pista. La bisagra engranada entrelazada permite ajustar y bloquear mecánicamente el ángulo de inclinación de la cámara a un ángulo preciso de 15 grados hacia abajo, evitando cualquier cambio no deseado en el lente causado por las vibraciones de alta frecuencia del chasis durante la operación. |
		| **MegaPi Case** <br><br><img width="400" height="400" alt="MegaPiBase (1)" src="https://github.com/user-attachments/assets/8db95bf2-a29a-468c-ace8-e21bb1fae9f6" /> | Una bandeja robusta de perfil bajo equipada con cuatro soportes verticales integrados de alta resistencia posicionados en las esquinas para asegurar el PCB principal. La placa base cuenta con guías de distribución internas y cortes de holgura estructural para evitar los componentes en la parte inferior de la placa, manteniendo el perfil lo más cercano posible al chasis. | Funciona como una cuna mecánica rígida para la electrónica de potencia de bajo nivel. Al elevar el PCB mediante los soportes integrados de 3 mm, evita cortocircuitos eléctricos con el chasis al tiempo que amortigua las vibraciones. El perímetro completamente abierto garantiza el acceso inmediato a los terminales de tornillo del motor, los rieles de alimentación y los puertos de sensores para el mantenimiento en campo. |
		| **RaspberryPi Base** <br><br><img width="400" height="400" alt="RaspberryPiBase (1)" src="https://github.com/user-attachments/assets/2403b708-2e1d-4360-9504-aae68c0027d1" /> | Una plataforma modular plana de nivel medio que cuenta con cuatro soportes de esquina integrados para montar la Raspberry Pi 4 de forma segura. La sección frontal de la base integra un montaje de bisagra de doble oreja equipado con dientes de bloqueo internos que se acoplan directamente con la bisagra de la carcasa de la cámara (Camera Case). | Sirve como un puente estructural de doble propósito. Proporciona un montaje estable y elevado para la computadora de a bordo de alto nivel, asegurando una disipación óptima del calor a través de la convección natural para evitar el estrangulamiento térmico del CPU. Al mismo tiempo, su montaje engranado integrado bloquea firmemente el ensamblaje de la cámara en la parte delantera, eliminando la necesidad de componentes adicionales y ahorrando valioso espacio en el chasis.|
		| **Ultrasonic Case** <br><br><img width="400" height="400" alt="UltrasonicSensorCase" src="https://github.com/user-attachments/assets/f9696c40-13e6-46b5-9712-2d7849a80005" /> | Un soporte protector compacto de doble barril hecho a medida para encapsular firmemente los cilindros del transmisor y receptor del módulo del sensor ultrasónico. Cuenta con pestañas de montaje traseras integradas y bridas inferiores para un acoplamiento mecánico continuo a las vigas transversales delanteras de la estructura del chasis. | Proporciona una carcasa rígida y aislada de vibraciones que mantiene el sensor ultrasónico perfectamente perpendicular al plano horizontal de la pista. Esta alineación precisa elimina la distorsión de la señal acústica y la dispersión de las ondas, garantizando mediciones de distancia en tiempo real altamente precisas para la detección de obstáculos y mapas de frenado de emergencia. |

		</div>

		- #### **Impresora:** Se usó las impresoras Creality Hi y Creality K1.

   			- **Creality Hi:** Es una de las propuestas más recientes de Creality, diseñada con un fuerte enfoque en competir directamente en el mercado de impresión multicolor accesible.
        
        		- **Volumen de construcción (lo que puedes imprimir):** $260 \times 260 \times 300\text{ mm}$. Es un tamaño intermedio-alto, excelente para robótica porque te permite hacer chasis completos en una sola pieza sin tener que segmentarlos.
            
          		- **Dimensiones de la máquina:** $409 \times 392 \times 477\text{ mm}$ (Peso: $8.75\text{ kg}$).
  
        		Es una impresora cartesiana de alta velocidad equipada con motores step-servo en los ejes X/Y para evitar la pérdida de pasos. Su gran fuerte es la compatibilidad nativa con el sistema CFS (Creality Filament System), un módulo externo tipo "banco de filamentos" que te permite alternar de forma automatizada hasta 4 colores diferentes (o hasta 16 si encadenas 4 módulos). Su velocidad máxima es de $500\text{ m/s}$ con una aceleración de $12,000\text{ mm/s}^2$ y alcanza los $300^\circ\text{C}$ en la boquilla.
  
        		- **¿Qué tan buena es?**
  
           			* **Puntos Fuertes:** Estructura de aluminio fundido extremadamente rígida, calibración y nivelación 100% automática por sensor de deformación, y detección inteligente de enredos o fin de filamento. Si compras la versión Combo (con el CFS), es una máquina brutal para piezas que necesitan soportes solubles o combinar materiales rígidos y flexibles.
  
       				* **Puntos Débiles:** Al no ser cerrada de fábrica (diseño abierto), imprimir materiales técnicos propensos a contraerse como el ABS o ASA de forma consistente puede ser complicado sin construirle una cabina externa.
          
	   			- **¿Se recomienda usarla a futuro?**
  
   					Sí, totalmente. Al ser una plataforma moderna, cuenta con el soporte de software más actualizado (Creality Print 5.1 / OrcaSlicer) y está diseñada bajo el ecosistema de cambio de filamento automático, que es hacia donde se mueve toda la industria. Es una excelente inversión a largo plazo para un taller.

			- **Creality K1:** Lanzada originalmente como la respuesta directa de Creality a la serie P1 de Bambu Lab, es una máquina de nivel profesional diseñada para velocidad pura y materiales exigentes.

     			- **Volumen de construcción (lo que puedes imprimir):** $220 \times 220 \times 250\text{ mm}$. Es un espacio estándar (ligeramente más pequeña que la Creality Hi).
        
    			- **Dimensiones de la máquina:** $355 \times 355 \times 480\text{ mm}$ (Peso: $12.5\text{ kg}$).
  
        		Utiliza un sistema cinemático CoreXY donde el cabezal se mueve de forma ultraligera en los ejes X/Y usando correas cruzadas, mientras la cama solo baja en el eje Z. Al estar completamente cerrada con paneles de vidrio y acrílico, retiene el calor interno en la cámara de impresión. Alcanza una velocidad de $600\text{ mm/s}$ y una aceleración masiva de $20,000\text{ mm/s}^2$ gracias a su firmware basado en Klipper (Creality OS).
  
   				- **¿Qué tan buena es?**
  
   					* **Puntos Fuertes:** Es una bestia para materiales técnicos. Su cámara cerrada es perfecta para imprimir PETG, ABS, ASA y Nylon sin sufrir warping (despegue de bordes). Su aceleración es casi el doble que la de la Creality Hi, reduciendo los tiempos de impresión de piezas mecánicas complejas drásticamente.
  
       				* **Puntos Débiles:** Las primeras unidades que salieron al mercado (lotes de 2023) sufrieron de problemas en el extrusor (versión V1) y en el hotend. Creality corrigió esto en las versiones posteriores (extrusor con palanca brillante y boquilla tipo Unicorn), por lo que si adquieres una hoy, te aseguras de tener la versión corregida y madura.
          
	   			- **¿Se recomienda usarla a futuro?**
  
   					Sí, pero bajo ciertas condiciones. Sigue siendo una máquina excepcionalmente rápida y robusta para piezas de ingeniería. Sin embargo, debes tener en cuenta que la K1 original no es compatible con sistemas de impresión multicolor multihilo modernos de manera nativa (esa característica se reservó para la serie K2 con el nuevo CFS).

		- #### **PETG vs PLA:**

		<div align="center">

		|  | PETG | PLA |
		|---|---|---|
		| **Durabilidad y Resistencia** | Alta durabilidad y tenacidad superior: Al estar modificado con glicol, el PETG impide la cristalización del polímero, resultando en un material altamente tenaz. Bajo esfuerzos mecánicos por impacto, sus cadenas moleculares tienen la flexibilidad necesaria para deformarse elásticamente y absorber la energía cinética del choque. Esto evita la propagación de grietas, haciéndolo ideal para piezas expuestas a colisiones continuas. | Baja durabilidad ante cargas dinámicas: El PLA posee una estructura molecular rígida y cristalina que le otorga una alta dureza superficial, pero carece de la capacidad de disipar energía de forma elástica. Ante colisiones directas o impactos bruscos contra los bordes de la pista, el material estresa sus uniones de capa interlace y tiende a la fractura frágil, quebrándose de manera repentina y catastrófica en lugar de flexionarse. |
		| **Resistencia y Estabilidad Térmica** | Excelente inmunidad térmica: Mantiene su integridad estructural y rigidez mecánica en entornos de trabajo de hasta 75°C a 80°C sin experimentar ablandamiento ni distorsión geométrica. Esta propiedad permite montarlo con total seguridad como soporte directo del tren motriz o de placas electrónicas, resistiendo el calor generado por la fricción mecánica y los picos de corriente sin ceder. | Vulnerable al estrés térmico: Su temperatura de transición vítrea (punto de ablandamiento) es críticamente baja, situándose entre los 50°C y 55°C. Si se utiliza en componentes en contacto directo con motores DC bajo carga pesada o reguladores de voltaje que disipan calor por conducción, el PLA pierde su rigidez rápidamente, sufriendo deformaciones geométricas permanentes que descalibran el chasis. |
		| **Rigidez Estructural y Flexión** | Módulo elástico moderado (Flexibilidad elástica): Posee una naturaleza semirrígida que le permite soportar vibraciones mecánicas, torsiones y cargas dinámicas continuas sin sufrir fatiga de material. Si bien cede ligeramente ante fuerzas extremas antes de romperse, esta flexibilidad estructural absorbe las oscilaciones del terreno, protegiendo los componentes internos. | Módulo elástico muy elevado (Rigidez absoluta): Presenta una resistencia a la flexión superior, lo que significa que no se dobla ni se deforma bajo cargas estáticas moderadas. Esta ausencia de flexibilidad elástica es una ventaja técnica para piezas estáticas del robot que requieren mantener una posición fija e invariable, neutralizando cualquier flexión parasitaria o pandeo. |
		| **Resistencia Química y Ambiental** |  Alta inercia química e hidrofobicidad: Es químicamente inerte y exhibe una resistencia sobresaliente ante aceites, grasas, lubricantes mecánicos y alcoholes de limpieza. Al ser completamente hidrofóbico, no se debilita por la humedad ambiental tras su impresión y su alta estabilidad frente a la radiación UV garantiza que las piezas mantengan sus propiedades mecánicas intactas. | Sensible a la degradación a largo plazo: Al ser un biopolímero derivado de fuentes orgánicas, es propenso a la degradación acelerada bajo la exposición continua a rayos UV o cambios de humedad drásticos. Además, su resistencia química frente a agentes externos como alcoholes, aceites o lubricantes de hardware es limitada, lo que puede debilitar las paredes de la pieza con el tiempo. |
		| **Precisión Dimensional y Encajes** | Tolerancias moderadas y propenso a hilos: Al requerir temperaturas de extrusión más altas, el material experimenta una mayor contracción térmica al enfriarse, lo que exige calibrar el flujo para evitar variaciones dimensionales en encajes milimétricos. Además, su alta viscosidad tiende a generar stringing (hilos finos) que requieren postprocesado en zonas de movimiento mecánico fino. | Tolerancias geométricas perfectas: Debido a su bajísima contracción térmica al enfriarse, el PLA destaca por una estabilidad dimensional milimétrica. Permite imprimir roscas, encajes de rodamientos y uniones mecánicas finas con errores de tolerancia prácticamente nulos, asegurando que las piezas encajen de manera exacta y sin holguras desde el primer prototipo. |
	
		</div>

# 2. Componentes <a id="sistemas-electronicos"></a>

- ### Precios:


El enfoque de nuestro prototipo es que el robot sea de bajo coste y sea más pequeño a diferencia del que utilizamos a principio de año y de esta forma podemos comparar precios

<div align="center">

**Versión Actual**

| Cantidad | Productos | Precio | Total |
|---|---|---|---|
| 1 | [Raspberry Pi Zero 2W](https://www.amazon.com/-/es/Raspberry-Pi-Zero-2W-inal%C3%A1mbrico/dp/B0C9TW4BNK) | $90 | $90 |
| 1 | [URGENEX Lithium-ion Battery](https://www.amazon.com/URGENEX-2000mAh-Battery-Rechargeable-Helicopter/dp/B0CJNNMST2) | $22 | $22 |
| 2 | [Servo SG90](https://www.amazon.com/engranaje-direcci%C3%B3n-adecuado-control-helic%C3%B3ptero/dp/B09J86CD22) | $8 | $8 |
| 1 | [Mini Micro N20 Motor](https://www.amazon.com/-/es/Acxico-unids-engranajes-velocidad-completo/dp/B09DG3GCGK) | $10 | $10 |
| 4 | [DRV8833 Dual Motor Driver](http://pololu.com/product/2130) | $11 | $11|
| 1 | [Arducam 8MP IMX219 Camera Module](https://www.amazon.com/-/es/Arducam-M%C3%B3dulo-Raspberry-distorsi%C3%B3n-compatible/dp/B09VSRH14M?th=1) | $20 | $20 |
| 1 | [Mini360 Mini 360 3A DC-DC)](https://www.amazon.com/-/es/Mini360-Aumento-Convertidor-Potencia-Boost-Down/dp/B0D3QSYRFT) | $15 | $15 |
| 1 | [Crash Collision Sensor Module](https://www.amazon.com/-/es/Generic-detecci%C3%B3n-colisi%C3%B3n-interruptor-Arduino/dp/B0D6GZDV95) | $5.54 | $5.54 |
| 1 | [Gikfun in Touch Switch](https://www.amazon.com/-/es/Gikfun-Interruptor-0-472x0-472x0-287-moment%C3%A1neo-colores/dp/B01E38OS7K/) | $10| $10 |
| | | | **$191.54** |

**Antigua previa**

| Cantidad | Productos | Precio | Total |
|---|---|---|---|
| 1 | [Raspberry Pi 4 B](https://www.amazon.com/Raspberry-Model-2019-Quad-Bluetooth/dp/B07TC2BK1X) | $123.99 | $123.99 |
| 1 | [Yfrobot steering chassis](https://yfrobot.com/products/steering-gear-robot) | $118.50 | $118.50 |
| 2 | [Zeee 3S Lipo Battery 2200mAh 11.1V 50C](https://www.amazon.nl/Zeee-Vrachtwagen-Vliegtuig-Quadcopter-Helikopter/dp/B0C2CHMCC3) | $50.65 | $50.65 |
| 1 | [Arducam 8MP IMX219 175°](https://www.amazon.com/Arducam-IMX219-Degree-Raspberry-Compatible/dp/B09VSVB4DT/ref=sr_1_7?crid=10W18P0RVDUOR&s=electronics&sr=1-7) | $26.99 | $26.99 |
| 4 | [Lever wire connectors](https://www.amazon.com/Conductor-Compact-Connectors-Electrical-Terminals/dp/B0D9Y5XFQC/ref=sr_1_2_sspa?sr=8-2-spons) | $9.99 | $9.99|
| 1 | [Buck Converter 3A 15W Type-C](https://www.amazon.com/-/es/Convertidor-Impermeable-Adaptador-corriente-compatible/dp/B0D2MTJQK8) | $8.79 | $8.79 |
| 1 | [MAKEBLOCK MegaPi (from mbot mega)](https://www.robotshop.com/products/makeblock-mbot-mega-robot-car-rechargeable-li-po-battery-kit?qd=c181467e2368e663479ab211142e2920) | $148.97 | $148.97 |
| 1 | [Crash Collision Sensor Module](https://www.amazon.com/-/es/Generic-detecci%C3%B3n-colisi%C3%B3n-interruptor-Arduino/dp/B0D6GZDV95) | $5.54 | $5.54 |
| 1 | [LED Traffic Light Module](https://www.amazon.com/Traffic-Light-Module-Board-Arduino/dp/B07R1KJ4DT) | $10.99| $10.99 |
| | | | **$504.41** |

</div>

- ### Descripción:

<div align="center">

| Foto | Descripción |
|---|---|
| **Raspberry Pi Zero 2W** <div  align="center"> <div  style="width:290 px"> <img width="466" height="227" alt="51nIyTxfaQL _AC_SX466" src="https://github.com/user-attachments/assets/68e57edf-f712-4b01-b716-4459a832151a" /> </div> </div>  | Se ha seleccionado la Raspberry Pi Zero 2W como el cerebro de procesamiento de alto nivel debido a su factor de forma ultra compacto y ligero permite integrarla fácilmente en chasis con restricciones espaciales estrictas (como vehículos autónomos a escala) sin comprometer la capacidad de ejecutar tareas complejas de visión por computadora con OpenCV (procesamiento de imágenes, detección de contornos o calibración por espacios de color en tiempo real) y comunicación serial fluida con microcontroladores secundarios, manteniendo además una excelente relación calidad-precio y un consumo energético eficiente para sistemas móviles alimentados por batería. |
| **URGENEX Lithium-ion Battery** <div align="center"> <img width="466" height="511" alt="71hyN7C7cyL _AC_SX466" src="https://github.com/user-attachments/assets/87c113c3-e2ff-4e0e-89fa-203eb6924d54" /> </div> | Se ha seleccionado la batería URGENEX (configuración 2S de 7.4V) como la fuente de alimentación principal del sistema debido a su excelente relación entre densidad energética, peso ligero y factor de forma compacto, lo que permite alojarla sin inconvenientes en compartimentos de chasis reducidos. Su capacidad de entrega de corriente constante garantiza una alimentación estable y libre de caídas de tensión repentinas para los sistemas de procesamiento de alto nivel (como la Raspberry Pi) y los controladores de motores, previniendo reinicios inesperados del sistema durante picos de aceleración o exigencia mecánica. Además, su alta tasa de descarga y su prolongada vida útil por ciclos de carga aseguran una autonomía óptima durante las pruebas de rendimiento y validación del robot. |
| **Servo SG90** <div  align="center"> <img width="522" height="522" alt="51Fh0G9sO+L _SX522" src="https://github.com/user-attachments/assets/4f3b3663-a6a0-442f-b0ed-0c96d0162d08" /> </div> | Se seleccionó la placa **Makeblock MegaPi** (**ATmega2560**) como microcontrolador central por su capacidad para gestionar múltiples motores y sensores simultáneamente, superando a opciones como Arduino Uno o Nano gracias a sus interfaces plug-and-play. Aunque está diseñada para acoplarse directamente sobre una Raspberry Pi, se optó por conectarla únicamente vía **USB** para la transferencia de datos. Esta alternativa optimiza el espacio del chasis, aprovecha que la MegaPi cuenta con alimentación propia y evita exponer la placa principal a riesgos durante el proceso de soldadura. |
| **Zeee 3S Lipo Battery 2200mAh 11.1V 50C** <div  align="center"> <div  style="width:290 px"> ![LX2-BUSB](https://m.media-amazon.com/images/I/71-SIfPk3XL._AC_UF1000,1000_QL80_.jpg) </div> | El robot utiliza una batería LiPo Zeee 3S (2200mAh, 11.1V, 50C) como fuente de energía única, elegida por su alta tasa de descarga y un diseño compacto que optimiza el espacio en el chasis frente a opciones más voluminosas. Esta configuración simplifica el sistema al alimentar tanto la lógica como los motores, aunque exige el uso de reguladores de voltaje externos (como convertidores CC-CC) para proteger componentes sensibles como la Raspberry Pi. A pesar de requerir un manejo cuidadoso con cargadores específicos para evitar riesgos y prolongar su vida útil, ofrece un balance excelente entre potencia, tamaño y rendimiento para aplicaciones robóticas. |
| **Steering servo mg996r** <div  align="center"> ![L298N](https://cdn-global-hk.hobbyking.com/media/catalog/product/cache/10/image/9df78eab33525d08d6e5fb8d27136e95/6/2/6221_1_high_7_.jpg) </div> | Incluido en el kit de YFROBOT para controlar el eje de dirección, el MG996R es un servomotor digital de alto torque que opera mediante señales PWM en un rango de 0° a 180°. Su piñonería metálica le otorga una mayor durabilidad y fuerza frente a los servos de plástico, permitiéndole soportar cargas mecánicas exigentes. Con un rango de operación de 4.8V a 6V, ofrece un torque de entre 9.4 y 11 kg·cm y velocidades de hasta 0.15 segundos por cada 60°, utilizando una interfaz estándar de tres pines totalmente compatible con microcontroladores como Arduino y Raspberry Pi. |
| **RS380 motor** <div  align="center"> ![motor](https://novatronicec.com/wp-content/uploads/2020/10/Motor-con-caja-reductora-25GA370_2.jpg) </div> | El conjunto de motor RS-380 con caja reductora es un sistema de corriente continua compacto y versátil, ideal para robótica pequeña y automatización ligera. Por sí solo, el RS-380 es un motor con escobillas de tamaño reducido que gira a altas revoluciones (entre 10 000 y más de 20 000 RPM según el voltaje) pero genera muy poco torque. La incorporación de la caja reductora soluciona esta limitación al disminuir la velocidad de giro mediante una serie de engranajes, lo que incrementa significativamente el torque de salida y permite al sistema mover cargas mecánicas más pesadas de manera práctica. |
| **ArduCam IMX219 8MP** <div  align="center"> ![Encorder](https://cdn.arducam.com/wp-content/uploads/2022/04/Arducam_IMX219_MIPI_Pi_B0392-8.jpg) </div> | La ArduCam IMX219 de 8MP es un módulo de cámara compacto basado en el sensor Sony IMX219, el mismo estándar de la Raspberry Pi Camera v2, que equilibra resolución y rendimiento para proyectos de visión artificial y robótica. Se conecta mediante la interfaz CSI (Camera Serial Interface), lo que garantiza una transferencia de datos a alta velocidad y con baja latencia hacia computadoras como Raspberry Pi o Jetson Nano. Este diseño la convierte en una solución eficiente y de fácil integración para sistemas embebidos que requieren procesamiento de imagen en tiempo real. |
| **Buck Converter 3A 15W Type-C** <div  align="center"> ![camera](https://m.media-amazon.com/images/I/61pOfxNxUnL._AC_UF1000,1000_QL80_.jpg) </div> | El módulo **convertidor buck tipo C de 3A y 15W** es un regulador reductor de CC-CC que transforma voltajes de entrada elevados en una salida baja y estable con una eficiencia del 85 al 95%. En este proyecto, se utilizó para conectar la batería **LiPo Zeee 3S** (de hasta 12.6V) a la **Raspberry Pi 4B**, la cual exige un suministro constante de **5V y hasta 3A**. Debido a que el voltaje directo de la batería dañaría la placa, el convertidor reduce y regula la tensión de manera segura, protegiendo los componentes contra sobrevoltajes, minimizando las pérdidas de energía por calor y garantizando un rendimiento estable del sistema a medida que la batería se descarga. |
| **Ultrasonic Sensor HC-SR04** <div  align="center"> <img width="466" height="466" alt="61CXJgLZwUL _SX466_" src="https://github.com/user-attachments/assets/1345b129-76f7-4f39-8ec2-b839398ea61b" /> </div> | El sensor ultrasónico HC-SR04 es un dispositivo compacto de medición de distancia que opera bajo el principio del eco de sonar, ideal para la evasión de obstáculos en robótica. Está equipado con dos transductores que emiten una ráfaga de ondas de alta frecuencia ($40\text{ kHz}$) y reciben su rebote tras chocar con un objeto. Al calcular con precisión el tiempo que tarda la señal en ir y venir, el módulo determina la distancia lineal en un rango efectivo de 2 a 400 centímetros con una precisión de 3 milímetros, proporcionando datos en tiempo real cruciales para la navegación del vehículo.|

</div>

- ### Disposición de Componentes y Justificación:

	El diseño de nuestro vehículo autónomo se fundamenta en una arquitectura modular de tres niveles verticales, optimizada para la gestión eficiente del centro de gravedad, el balance de masas y la mitigación de interferencias electromagnéticas y mecánicas. Esta configuración jerárquica por "pisos" permite aislar los elementos mecánicos de potencia frente a los módulos lógicos de procesamiento y visión artificial.

	- Arquitectura del Chasis por Niveles:

	- 1st Level (Planta Baja):
	Constituye la base estructural y el tren de rodaje del vehículo. En este nivel se ubica el Motor de Tracción RS380, el mecanismo de dirección asistido por el servomotor, y los tres sensores ultrasónicos HC-SR04 (Front-US y los sensores laterales Left-US / Right-US).

		- Justificación Técnica: Colocar los actuadores más pesados y el sistema de tracción en la planta baja garantiza un centro de gravedad lo más cercano posible al suelo, proporcionando estabilidad cinemática y tracción máxima en las ruedas traseras durante aceleraciones bruscas.

	- 2nd Level (Planta Intermedia):
Situado inmediatamente arriba de la transmisión, este nivel alberga el núcleo de control de bajo nivel y la distribución eléctrica principal. Aquí se encuentran fijadas la placa de expansión Makeblock MegaPi, el Buck Converter (3A 15W) y la jaula vertical contenedora de las Baterías LiPo.

		- Justificación Técnica: La MegaPi actúa como puente físico intermedio para acortar las trayectorias del cableado hacia los motores del primer nivel. Al centralizar las baterías pesadas en este piso medio y alineadas horizontalmente con el centro de masa, se reducen los momentos de inercia polares, evitando subvirajes o sobrevirajes en las curvas cerradas de la pista. El Buck Converter se sitúa estratégicamente al lado de la MegaPi para reducir y estabilizar el voltaje proveniente de las celdas antes de enviarlo al nivel superior.

	- 3rd Level (Planta Superior):
	Corresponde a la cúspide de la estructura, dedicada de forma exclusiva al procesamiento de alto nivel y la percepción geométrica. Contiene la computadora a bordo Raspberry Pi 4 B (equipada con su disipador térmico y ventilador activo) y el conjunto elevado de la cámara de visión artificial Arducam IMX219.

		- Justificación Técnica: Elevar la Raspberry Pi 4 la aísla por completo de las vibraciones mecánicas directas del motor de tracción y de los bucles de corriente del chasis inferior. Asimismo, la posición superior favorece la convección térmica del ventilador para evitar el estrangulamiento térmico (thermal throttling) del CPU durante la ejecución de los algoritmos de detección.

	- Sistema de Percepción y Orientación Espacial:

	Esta distribución en tres dimensiones complementa la estrategia de nuestro sistema de percepción mixto, asegurando zonas de cobertura óptimas sin interferencias mutuas:

	- Distribución de Visión Artificial (3rd Level):
	La cámara Arducam IMX219 se posiciona en el punto más alto y adelantado del tercer nivel, sostenida por un brazo articulado impreso en 3D con un ángulo de inclinación fijo hacia abajo de 15 grados. Esta elevación es crítica para expandir la línea de visión del lente de 175°, permitiendo al algoritmo abarcar una Región de Interés (ROI) más amplia de la pista para identificar los códigos de color (semáforos) y líneas guía sin que la propia estructura del carro obstruya el encuadre.

	- Distribución Ultrasónica Frontal (1st Level):
	El sensor ultrasónico delantero (Front-US) se monta directamente sobre la placa base del chasis en una posición baja y avanzada, justo por debajo de la línea de proyección de la cámara. Esta sincronización geométrica permite que, mientras la cámara procesa las decisiones lógicas en el nivel superior, el ultrasonido actúe en el nivel inferior como un bypass de seguridad de hardware en tiempo real, detectando la presencia física de obstáculos de forma matemática y directa para activar frenados de emergencia.

	- Distribución Ultrasónica Lateral (1st Level):
	Los dos sensores ultrasónicos de flanco (Left-US y Right-US) están anclados rígidamente a los costados izquierdo y derecho del primer nivel, posicionados de forma longitudinal entre ambos ejes de ruedas y alineados verticalmente a la altura exacta de los neumáticos. Ubicarlos en el piso bajo, simétricos respecto al centro de masa, minimiza drásticamente las lecturas falsas causadas por el cabeceo (frenada) o el balanceo (giro) del chasis. Esto asegura que el algoritmo de estabilización reciba datos limpios y constantes de la distancia real hacia las paredes de la pista para mantener una trayectoria perfectamente recta.

<div align="center">

<img width="1600" height="1200" alt="WhatsApp Image 2026-06-18 at 11 34 59 PM" src="https://github.com/user-attachments/assets/5bea7abe-f434-4bbd-9ce3-3c26d1443c42" />

</div>

- ### Batería:

	La Zeee 3S LiPo 11.1V 2200mAh 50C es una batería de polímero de litio de alto rendimiento, diseñada específicamente para entusiastas del radiocontrol (RC) que buscan un equilibrio óptimo entre peso, tamaño y potencia. Con una configuración de 3 celdas (3S) y un voltaje nominal de 11.1V, este componente proporciona la energía constante y agresiva necesaria para impulsar una amplia variedad de modelos, desde drones de carreras y aviones a escala hasta vehículos terrestres RC. Su capacidad de 2200mAh asegura un tiempo de juego o vuelo sumamente competitivo, permitiendo exprimir al máximo el rendimiento del motor sin añadir un peso excesivo que pueda comprometer la agilidad del modelo.

	El verdadero punto fuerte de esta batería radica en su tasa de descarga de 50C, lo que significa que es capaz de entregar picos de corriente elevados de forma segura cuando el acelerador lo demanda, garantizando aceleraciones explosivas y una respuesta inmediata a los mandos. Fabricada con materiales de alta calidad y una baja resistencia interna, la Zeee 3S destaca por su ciclo de vida prolongado y su estabilidad térmica durante un uso intensivo. Viene equipada habitualmente con conectores de alta conductividad (como el Deans T o XT60) y un conector de equilibrado JST-XH, lo que facilita tanto una carga segura celda por celda como una compatibilidad directa con la mayoría de los cargadores inteligentes del mercado.

- ### Presupuesto de Energía:

	Para garantizar la estabilidad operativa de nuestro carro, hemos implementado una arquitectura de alimentación redundante mediante el uso de dos baterías independientes. Esta división es fundamental para proteger la integridad de nuestros sistemas:

	- **Circuito de Potencia:** Una batería dedicada exclusivamente a la placa MegaPi, la cual gestiona los actuadores de alta demanda (el motor de tracción RS380 y el servomotor de dirección MG996R), además de los tres sensores ultrasónicos y el botón de inicio. Este aislamiento evita que las caídas de tensión (transitorios) provocadas por los arranques repentinos o el bloqueo de los motores afecten el procesado de datos.

	- **Circuito de Lógica y Visión:** Una segunda batería independiente alimenta exclusivamente a la Raspberry Pi 4 y la cámara Arducam. Esta separación es crítica; al no compartir el bus de energía con los motores, eliminamos el riesgo de interferencia electromagnética (EMI) y picos de voltaje que podrían inducir ruido en la señal de video o, en el peor de los casos, provocar reinicios inesperados del sistema de visión artificial durante la competencia.

Esta configuración nos permite operar con la máxima seguridad, garantizando que, incluso bajo condiciones de estrés mecánico severo en la dirección y tracción, nuestro "cerebro" (Raspberry Pi) mantenga una alimentación constante y limpia para procesar la trayectoria con total precisión.

<div align="center">

| Componentes | Cantidad | Voltaje de Operación | Consumo Nominal/Pico | Consumo Total |
|---|---|---|---|---|
| **Raspberry Pi 4 B** | 1 | 5.0 V | 600 mA / 1250 mA | 1250 mA |
| **Arducam 8MP IMX219 (175°)** | 1 | 3.3 V (vía RPi) | 250 mA | 250 mA |
| **Makeblock MegaPi (Lógica)** | 1 | 5.0 V | 100 mA | 100 mA |
| **Sensores Ultrasonido HC-SR04** | 3 | 5.0 V | 45 mA (15 mA c/u) | 45 mA |
| **Módulo Sensor de Colisión (Crash)** | 1 | 5.0 V | 10 mA | 10 mA |
| **Módulo Semáforo LED (Traffic Light)** | 1 | 5.0 V | 30 mA | 30 mA |
| **Servomotor de Dirección MG996R** | 1 | 5.0 V | 500 mA / 2500 mA | 2500 mA |
| **Motor de Tracción RS380** | 1 | 6.0 V (vía Driver) | 1200 mA | 2000 mA |
| Total | | | 2,735 mA (2.73 A) mA | 6,185 mA (6.18 A) |

</div>

Conclusión del Presupuesto
El consumo total del sistema alcanza los 6.18 A en condiciones de carga máxima (stall). La arquitectura de doble batería es vital por dos razones:

- Protección de la Lógica: El circuito de Lógica (1.50 A) opera aislado de los transitorios electromagnéticos de los motores.

- Capacidad de Respuesta: El circuito de Potencia (4.68 A) está dimensionado para soportar los picos de corriente del servo y el motor de tracción simultáneamente. Esta división asegura que, aunque los actuadores alcancen su máximo esfuerzo mecánico, la Raspberry Pi mantenga un voltaje estable, evitando reinicios críticos durante la competencia.

- ### Diagrama de Cableado:

	La arquitectura eléctrica de nuestro carro ha sido diseñada bajo un principio de aislamiento de buses para garantizar la fiabilidad del sistema en un entorno de alta vibración y demanda de corriente. Como se observa en nuestro diagrama de conexiones, el cableado se divide en dos dominios claramente diferenciados:

	- Dominio de Potencia (Bus de Fuerza)
Alimentado por la batería dedicada a actuadores, este bus de alta corriente alimenta directamente la MegaPi para los motores y el servomotor:

		- MegaPi: Actúa como el centro de distribución de energía principal. Recibe el voltaje directo de la batería de fuerza (7.2V - 12V) para alimentar el motor de tracción RS380 y el servomotor de dirección MG996R en sus puertos dedicados.

		- Sistema de Tracción y Dirección: El motor RS380 y el servo MG996R están conectados directamente a los puertos de alta potencia de la MegaPi. Hemos utilizado cables de calibre superior para minimizar la caída de tensión (voltaje drop) durante las maniobras de stall (esfuerzo máximo).

		- Regulación y Estabilización de Voltaje (Buck Converter): Se ha integrado un Buck Converter de 3A y 15W con salida Type-C. Este módulo step-down se encarga de reducir de forma eficiente el voltaje de la batería y estabilizarlo a unos 5.0V constantes. Su función es actuar como una barrera de protección frente a los picos de consumo y el ruido eléctrico residual generados por los motores, asegurando un suministro de energía limpio y seguro para los componentes lógicos sensibles y los sensores ultrasónicos, evitando lecturas erráticas.

	- Dominio de Lógica (Bus de Control)
Alimentado por la batería dedicada a la Raspberry Pi, este bus es eléctricamente independiente:

		- Procesamiento de Datos: La Raspberry Pi 4 B alimenta la cámara Arducam a través del puerto CSI, asegurando un flujo de datos de baja latencia y alta integridad.

		- Comunicaciones (Bus I2C/UART): La comunicación entre la Raspberry Pi y la MegaPi se realiza mediante un puente serial (USB/UART) debidamente blindado. Para evitar "ground loops" (bucles de tierra) que son la principal causa de fallos en robots autónomos, hemos unificado las tierras (GND) solo en el punto de entrada de la MegaPi, manteniendo el resto del cableado de sensores con rutas cortas y directas para minimizar la captación de EMI (Interferencia Electromagnética).

<div align="center">

<img width="2960" height="1625" alt="L-N-M@1 25x" src="https://github.com/user-attachments/assets/13e15df3-6f13-4d22-9dfd-a9a075e6561c" />

</div>

# 3.  Software <a id="arquitectura-de-software"></a>

- ### Herramientas de apoyo:

	- **Color Detector:** Es una herramienta interactiva de calibración visual diseñada para segmentar y aislar colores específicos en tiempo real mediante el espacio de color LAB (Luminancia, A y B) y filtros de desenfoque gaussiano. El sistema captura el flujo de video de una Picamera2, aplica transformaciones morfológicas de erosión y dilatación para limpiar el ruido de la imagen, y genera una máscara binaria basada en umbrales máximos y mínimos ajustables por deslizadores en una interfaz gráfica (GUI) construida con CustomTkinter. Su función principal es preajustar firmas de color (como rojo, verde, azul o negro) y exportar estos rangos óptimos a un archivo de configuración JSON para que el robot pueda reconocer objetos o líneas de manera 	estable bajo diferentes condiciones de luz.

   	<div align="center">

	<img width="803" height="447" alt="Gemini_Generated_Image_oe7w1uoe7w1uoe7w" src="https://github.com/user-attachments/assets/8ed55c9c-b1f7-45c8-a92f-bee337e51ff2" />

	</div>

	- **ROI Detector:** Es una utilidad de configuración espacial basada en OpenCV que permite delimitar "Regiones de Interés" (ROI) personalizadas sobre la transmisión de video de la cámara mediante clics y arrastres del mouse. El script escala el fotograma original de forma proporcional dentro de un lienzo centrado con bordes negros constantes, permitiendo al usuario dibujar múltiples cuadrantes, visualizando dinámicamente sus dimensiones en píxeles. Su propósito principal es limpiar la memoria caché con la tecla 'C' o finalizar la captura con la tecla 'ESC' para activar una ventana flotante de Tkinter que exporta de forma automatizada las coordenadas $(x_1, y_1, x_2, y_2)$ estructuradas como una lista de objetos en un archivo nativo de Python (.py), aislando las zonas específicas de análisis visual donde el robot debe procesar la información (como la línea del suelo) e ignorando el ruido del entorno.

   	<div align="center">

	<img width="765" height="565" alt="Gemini_Generated_Image_fop2o1fop2o1fop2" src="https://github.com/user-attachments/assets/f9cc3741-7394-4642-af6d-1e69d5f4c231" />


	</div>

- ### MegaPiController:

	Esta es una descripción completa de todos los atributos y métodos de la clase, junto con sus argumentos. Te recomendamos que la consultes primero antes de pasar a las demás secciones y que, cuando clones el repositorio, la utilices como guía para orientarte en nuestro código.

  	Aquí tienes toda la documentación técnica completamente traducida al español, manteniendo exactamente el mismo formato y orden riguroso de las imágenes de referencia:

---

 **mega_pi_controller.py (clase MegaPiController)**

 **Dependencias**

* `serial`
* `time`
* `threading`
* `pandas`
* `random`
* `json`
* `cv2`
* `src.vision_controller.VisionController`
* `dataclasses.dataclass`

**Descripción del método constructor**

```python
def __init__(self, port='COM9', baudrate=115200):
    """
    Inicializa la conexión serial con la placa MegaPi y registra los subsistemas.
    Si la conexión falla, termina el proceso con un mensaje de error crítico.
    """

```

El constructor establece un canal de comunicación a través de puerto serial por hardware con el microcontrolador MegaPi. Inicia automáticamente un hilo de escucha en segundo plano (`_read_telemetry`) para capturar las métricas de hardware entrantes de forma asíncrona, inicializa el subsistema de visión artificial (`VisionController`), carga las máscaras de color predefinidas desde estructuras JSON específicas y prepara los registros internos, las variables de estado y las Regiones de Interés (ROIs) para el seguimiento espacial y de líneas.

<div align="center">

**Descripción de atributos:**

| Atributo | Tipo de dato | Funcionalidad |
| --- | --- | --- |
| `ser` | `serial.Serial` | Representa el canal de comunicación serial por hardware de bajo nivel con la MegaPi. |
| `dist_front` | `int` | Almacena el valor de distancia en tiempo real (cm) capturado por el sensor ultrasónico central. |
| `dist_left` | `int` | Almacena el valor de distancia en tiempo real (cm) capturado por el sensor ultrasónico izquierdo. |
| `dist_right` | `int` | Almacena el valor de distancia en tiempo real (cm) capturado por el sensor ultrasónico derecho. |
| `ir_left` | `int` | Almacena el valor porcentual bruto de reflectancia ($0\%$ a $100\%$) del sensor IR izquierdo TCRT5000. |
| `ir_right` | `int` | Almacena el valor porcentual bruto de reflectancia ($0\%$ a $100\%$) del sensor IR derecho TCRT5000. |
| `data_log` | `list[dict]` | Registro volátil en memoria utilizado para encolar los pasos de telemetría destinados al guardado de datos de entrenamiento. |
| `log_index` | `int` | Contador de pasos continuo auto-incrementable para el dataframe del registro de telemetría. |
| `vision` | `VisionController` | Módulo central instanciado responsable de las capturas de fotogramas y del mapeo de contornos LAB/HSV. |
| `running` | `bool` | Variable booleana de control de ejecución de alto nivel utilizada para terminar de forma segura las operaciones del hilo en segundo plano. |
| `reader_thread` | `threading.Thread` | Hilo de trabajo daemon asíncrono dedicado a sondear los paquetes de carga útil serial entrantes. |
| `button_value` | `int` | Representación binaria del estado del botón físico integrado en la placa para el inicio del sistema. |
| `turning_direction` | `int` | Rastrea la configuración del diseño del carril ($0$: No asignado, $1$: Sentido horario/Azul, $2$: Sentido antihorario/Naranja). |
| `rois` | `list[ROI]` | Define cuadros de procesamiento fijos en código para el análisis del área de la pared frontal y las líneas de la pista. |

</div

**Descripción de métodos:**

<div align="center">

| Método | Argumentos | Retorno | Descripción |
| --- | --- | --- | --- |
| `_read_telemetry()` | Ninguno | `None` | Hilo de trabajo de sondeo continuo. Decodifica un formato de carga útil rígido de 8 bytes prefijado por un byte de cabecera `0xAA`. |
| `_send_command()` | `action: int`, `v1: int`, `v2: int` | `None` | Empaqueta y transmite instrucciones de protocolo de control de bajo nivel de 5 bytes prefijadas con una bandera de comando `0xFF`. |
| `get_masks()` | `color: str` | `list` | Abre los archivos de configuración local de matrices de color y extrae los arreglos de límites numéricos. |
| `load_masks()` | Ninguno | `None` | Método de arranque secuencial que mapea los límites de los colores rojo, verde, azul, naranja y negro dentro del objeto. |
| `obtenerarea_frontal()` | Ninguno | `None` | Consulta los volúmenes de masa de contornos negros a lo largo de la ROI del horizonte frontal superior. |
| `obtener_linea_azul()` | Ninguno | `None` | Segmenta y evalúa el perfil del diseño de la línea de seguimiento buscando activadores de la pista azul. |
| `obtener_linea_naranja()` | Ninguno | `None` | Segmenta y evalúa el perfil del diseño de la línea de seguimiento buscando activadores de la pista naranja. |
| `debug_UI()` | Ninguno | `None` | Motor de superposición gráfica que muestra los bucles de seguimiento dinámico de visión artificial en una ventana de fotograma local. |
| `log_step()` | `action_code: int` | `None` | Añade los valores de las variables en tiempo real (ultrasónicos, infrarrojos) al arreglo del registro local. |
| `move_forward()` | `speed: int`, `log: bool` | `None` | Invoca los actuadores de tracción de bajo nivel para fijar la marcha hacia adelante a las velocidades seleccionadas. |
| `move_backward()` | `angle: int`, `speed: int`, `log: bool` | `None` | Activa vectores de movimiento en reversa mientras fija los eslabones de dirección a un ángulo de escape. |
| `turn_direction()` | Ninguno | `None` | Macro de control reactivo que enruta los pasos de giro basándose en los estados actuales de dirección. |
| `turn_left()` | `angle: int`, `speed: int`, `log: bool` | `None` | Ajusta los eslabones del servo mecánico Ackermann a ángulos cerrados hacia la izquierda bajo velocidades de tracción fijas. |
| `turn_right()` | `angle: int`, `speed: int`, `log: bool` | `None` | Ajusta los eslabones del servo mecánico Ackermann a ángulos cerrados hacia la derecha bajo velocidades de tracción fijas. |
| `turn_center()` | `log: bool` | `None` | Recalibra los pulsos del servo de dirección activa de vuelta a las coordenadas del centro geométrico. |
| `stop()` | `log: bool` | `None` | Desactiva los registros de velocidad activos de inmediato para cortar la energía de los motores y detener el vehículo. |
| `get_distances()` | Ninguno | `tuple[int, int, int]` | Getter estándar de telemetría que devuelve una tupla compuesta por las métricas actuales de los sensores (frontal, izquierdo, derecho). |
| `get_ir_reflectance()` | Ninguno | `tuple[int, int]` | Devuelve una tupla en tiempo real que contiene los porcentajes de reflectividad infrarroja localizada ($0-100\%$). |
| `save_data_to_csv()` | `filename: str` | `None` | Compila los volcados de datos encolados directamente en estructuras mapeadas por índices en el disco a través de Pandas. |
| `close()` | Ninguno | `None` | Libera los manejadores de procesos, envía un comando de parada total y cierra de forma segura los puertos seriales abiertos. |
| `start()` | Ninguno | `bool` | Evalúa los estados del botón. Devuelve `True` si el botón está liberado (HIGH/0), manteniendo el bucle en ejecución. |

</div>

- ### Arduino Controller:

	- Open Challenge:
  
		- **Open Challenge Video:**

		<div align="center">
			
		[![Open Challenge Video](https://img.youtube.com/vi/WPSj0BXfQ5U/0.jpg)](https://youtu.be/WPSj0BXfQ5U)

		*Demonstrates autonomous navigation and speed control on a dynamic track.*

		</div>

		- **Estrategia:** Para cumplir con los desafíos del Open Challenge, se diseñó e implementó una arquitectura de software basada en un bucle de control de alta frecuencia. La estrategia central no depende de un solo sensor, sino de un Control Híbrido (Sensor Fusión) que alterna dinámicamente entre la Visión Artificial (cámara) y la Telemetría Acústica (sensores ultrasónicos) según las condiciones de la pista. El sistema se divide en cuatro pilares de ejecución: Detección de Sentido, Control de Trayectoria (PIDs independientes), Navegación en Esquinas y Seguridad Activa (Anticolisión).
		
		- **ROIS:** Para optimizar el procesamiento computacional, mantener un alto framerate y evitar falsos positivos con elementos externos a la pista, el campo de visión de la cámara se segmenta geométricamente:
 
			- ROI Principal (Búsqueda de Color): Un recuadro amplio (0, 50, width, height-100) dedicado exclusivamente a procesar máscaras de color (Rojo, Verde, Azul, Naranja) mediante la búsqueda de contornos.

			- ROIs Laterales (Centrado Visual): El espacio inferior se divide en dos cuadrantes simétricos, roi_izq y roi_der. Estas regiones aplican una máscara negra (mask_black) para calcular en tiempo real el área en píxeles de las paredes laterales de la pista, permitiendo que el algoritmo sepa matemáticamente hacia qué lado está más inclinado el chasis.

		- **Contador de Loops:** En los instantes iniciales de la carrera, el robot ejecuta ciclos de evaluación (loops de detección) para procesar el área de los colores clave que dictan la dirección del circuito. Si en estos loops el sistema detecta un área mayor a un umbral crítico de 1200 píxeles de color Naranja, la variable de estado asume una orientación de giro a la derecha; si el umbral se rompe con el color Azul, el sistema bloquea la lógica para girar a la izquierda durante el resto de las vueltas.

		- **Diagrama de Flujo:**

	<div align="center">

	<img width="3505" height="4877" alt="untitled (1)" src="https://github.com/user-attachments/assets/94f21db8-a8a3-445f-988f-bbd1e25d0978" />

	</div>

	- **Obstacle Challenge:**

	La estrategia diseñada para abordar el segundo reto (evasión de obstáculos) se construye de forma modular sobre la base arquitectónica de la ronda abierta. Se conservan las Regiones de Interés laterales (roi_izq y roi_der), la resolución de la cámara y los filtros de segmentación de color base.
El núcleo de este reto radica en la interpretación semántica del entorno según las reglas oficiales de la competencia: los pilares actúan como señales direccionales que indican el carril de paso correcto. Para cumplir con esta lógica de navegación de manera robusta a una velocidad constante (VELOCIDAD_BASE = 68), el software se estructuró sobre tres pilares fundamentales:
Base del Reto Abierto (Navegación Línea Base): Conserva el control de centrado mediante la diferencia de áreas de líneas y el fallback de seguridad asistido por ultrasonidos.
Técnica de Selección de Carril (Visión Computacional): Segmentación por color a larga distancia mediante una nueva Región de Interés frontal expandida (ROI_OBSTACULOS).
Máquina de Estados Asíncrona: Algoritmos de control dedicados para la evasión precisa y el retorno seguro al carril.

	Para anticipar la trayectoria de los pilares sin interferir con la lectura de las líneas guía del suelo, se implementó una zona de escaneo central denominada ROI_OBSTACULOS con dimensiones optimizadas en píxeles ROI(30, 30, 610, 320). Esta configuración permite procesar los objetos antes de que entren en el umbral crítico de colisión frontal.
Adicionalmente, el sistema implementa dos lazos de control PID independientes con sintonizaciones diferenciadas según las necesidades dinámicas del vehículo:
PID de Línea Estándar: Configurado con valores conservadores (Kp = 0.015, Kd = 0.035) para mantener transiciones suaves y un desplazamiento lineal estable en rectas.
PID de Evasión de Obstáculos: Configurado con una respuesta altamente agresiva (Kp = 0.32, Kd = 0.01). El término proporcional elevado garantiza que el vehículo responda con un torque de dirección inmediato ante el desplazamiento del pilar en la imagen, mientras que el término derivativo amortigua el retorno para evitar que la parte trasera del chasis (cola) derrape y golpee el obstáculo.

	- 2. Implementación de la Máquina de Estados de Navegación
	El comportamiento dinámico de Halbi the Green se rige por una máquina de estados finitos que conmuta de forma asíncrona entre tres modos de operación para asegurar que las lógicas de centrado y evasión no entren en conflicto.

		- Estado 1: LINEAL (Navegación Base y Curvas Cerradas)
		Es el estado por defecto del robot. Mientras se encuentra en este modo, el vehículo ejecuta de forma prioritaria el centrado geométrico calculando el error entre las áreas negras laterales (error = black_areas[1] - black_areas[0]). Si el sensor de ultrasonido frontal detecta una pared a corta distancia (front_dist < 90 cm) en copresencia con una alta densidad de pixeles negros de pista (LNM.black_area > 8000), el estado se bloquea temporalmente bajo la bandera girando = True para forzar un giro de esquina cerrada de 90°. De manera simultánea, el método procesar_obstaculos() analiza los contornos máximos filtrados bajo las máscaras mask_red y mask_green. La transición hacia el estado de evasión se activa inmediatamente cuando el área de un contorno supera los umbrales de ruido calibrados:

		<div align="center">
		
		**Pilar Verde: Área $> 350 \text{ px} \rightarrow$ Transición a ESQUIVANDO | memoria_lado = "IZQUIERDA" (El pilar se debe dejar a la izquierda).**
		**Pilar Rojo: Área $> 300 \text{ px} \rightarrow$ Transición a ESQUIVANDO | memoria_lado = "DERECHA" (El pilar se debe dejar a la derecha).**

		</div>
		
		- Estado 2: ESQUIVANDO (Lazo de Control de Evasión)
		Al entrar en este modo, el PID de líneas se suspende y el control de dirección pasa al lazo PID de obstáculos. El algoritmo persigue un Setpoint o punto de consigna absoluto en los extremos del cuadro visual para forzar al carro a abrirse hacia el carril libre:

		<div align="center">
		
		**Para pilares verdes (dejar a la izquierda), se busca el SETPOINT_VERDE = 549 (extremo derecho del marco).**

		**Para pilares rojos (dejar a la derecha), se busca el SETPOINT_ROJO = 50 (extremo izquierdo del marco).**

		- Mecanismo de Tiempo de Gracia: Debido a la agresividad del giro, es común que el pilar salga del campo visual de la cámara antes de que el vehículo lo haya superado físicamente.

		Para evitar que el robot regrese prematuramente al centro de la pista y colisione con el obstáculo, se implementó un temporizador de inercia (TIEMPO_GRACIA = 0.2 segundos). Si el área del pilar cae a cero, el sistema mantiene el cálculo del último error registrado (error_obs = prev_error), sosteniendo el ángulo de giro por hardware durante el tiempo de gracia antes de conmutar al estado REBASANDO.

		- Seguridad por Encajonamiento: Si los sensores ultrasónicos detectan que el vehículo se está aproximando peligrosamente a la pared exterior del circuito debido a la maniobra de esquiva (left_dist o right_dist < DIST_MIN_PARED de $18.0\text{ cm}$), la máquina aborta el lazo PID de visión y fuerza la transición inmediata al estado de rebase para proteger la integridad estructural.
  
		- Estado 3: REBASANDO (Zona de Seguridad y Retorno)
		Este estado garantiza que la parte posterior del chasis rebase completamente el pilar antes de restablecer las condiciones de carrera lineal. Dado que la cámara ya no posee contacto visual con el obstáculo, el control se delega a la telemetría de los sensores ultrasónicos laterales. El vehículo mantiene un ángulo de compensación controlado según el lado memorizado para evitar rozar la pared lateral. La máquina de estados no permite el regreso al modo LINEAL hasta que el sensor de ultrasonido del lado opuesto al pilar registre una distancia libre mayor a $40\text{ cm}$ (left_dist > 40 o right_dist > 40). Esta holgura asegura de forma matemática que el volumen total del robot ha despejado la posición del pilar, evitando enganches con las esquinas traseras o la base del obstáculo.

		Como última capa de protección ante pérdidas de tracking visual o escenarios de colisión inminente, el ciclo de control ejecuta en cada iteración una subrutina de freno de mano físico. Si el ultrasonido frontal registra una distancia menor a DIST_MIN_CHOQUE ($12.0\text{ cm}$), el vehículo interrumpe la energía de los motores mediante LNM.stop() y calcula un ángulo de escape inverso de manera dinámica:

		<div align="center">
	
		$$\text{Ángulo Escapatoria} = 160^\circ - \text{steering\_angle}$$

		</div>
	

		El robot realiza una maniobra de retroceso a alta potencia (speed = 85) durante $0.75$ segundos, resetea las variables integrales del PID a cero y reestablece el estado de carrera a LINEAL, garantizando la resiliencia del software ante condiciones críticas de atasco ambiental.


		- **Diagrama de Flujo:**
 
	<div align="center">

	<img width="3533" height="5354" alt="untitled" src="https://github.com/user-attachments/assets/9ba2ee32-f8ed-4207-aa86-ce3b5ed009fa" />

	</div>

# 4. Challenges

- ### Problemas de Hardware:

	**Objetivo:** Completar tres vueltas de forma autónoma en circuitos configurados dinámicamente.

	### Problemas de espaciamiento

	Durante el desarrollo temprano de *Halbi the Green*, se presentaron inconvenientes con respecto al posicionamiento de los componentes dentro del chasis base (sin modificar). Debido a que los componentes ocupaban más espacio del disponible, el problema se resolvió temporalmente fijándolos con cinta aislante. Aunque esto funcionó de forma provisional, no era una solución viable a largo plazo. 

	Por ello, se decidió implementar una serie de bases impresas en 3D pensadas para agregar **dos niveles adicionales** al vehículo y **tres soportes complementarios** (dos laterales y uno frontal) para ubicar los sensores de ultrasonido, los cuales originalmente no tenían un lugar asignado.

	De manera más específica, los problemas de espaciamiento y sus respectivas soluciones fueron los siguientes:

	- **Espacio ocupado por las baterías:**

		- * *Problema:* Ocupaban demasiado volumen en el chasis y no dejaban espacio para ubicar los componentes de forma cómoda.

    	- *Solución:* Se les diseñó una base a medida para ubicarlas en el centro del robot y, sobre esta estructura, se construyó el piso superior.
       
	- **Anclaje de sensores de ultrasonido:**
   
		- *Problema:* No tenían puntos previstos para anclarlos al chasis original.

    	- *Solución:* Se diseñaron 3 bases impresas que van adjuntas a 3 caras del chasis.
      
    - *Nota técnica:* Esta solución no fue del todo ideal, ya que estas bases sobresalen un poco de la estructura, causando atascamientos mecánicos cuando el vehículo pasa muy cerca de una esquina.
      
	* **Ubicación de la cámara y controlador:** * *Problema:* No había lugar físico para situar la cámara ni la placa de procesamiento.
  
    	* *Solución:* Sobre la base de las baterías se diseñó un soporte dedicado para la Raspberry Pi y la cámara. Esta última incluye una base con ángulo graduable para poder ajustar el punto de vista del lente de manera cómoda y precisa.

	### Problemas con las conexiones (Cableado)

	* **Problema:** Al tener cables sueltos y expuestos, estos se quedaban atascados constantemente con el entorno e incluso se llevaban por delante los obstáculos del circuito en algunas ocasiones.
  
	* **Solución:** Se reorganizaron por completo las conexiones para eliminar los bucles y partes sobresalientes del cableado.
  
- ### Problemas de Software:

	- a
