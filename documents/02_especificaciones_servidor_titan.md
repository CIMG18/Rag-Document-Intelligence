# Ficha Técnica: Servidor de Alta Densidad Titan-X9000

## 1. Arquitectura de Procesamiento y Memoria
- **Procesador Central**: Equipado con dos procesadores AMD EPYC 9654 Genoa de 96 núcleos cada uno (192 núcleos y 384 hilos en total), con una frecuencia base de 2.4 GHz y modo turbo de hasta 3.7 GHz.
- **Caché L3**: Dispone de 384 MB de caché L3 por socket (768 MB en total para el chasis).
- **Memoria RAM**: 24 ranuras DIMM DDR5-4800 MHz ECC registradas. Capacidad instalada de 1.5 TB, escalable hasta 6 TB por nodo. Ancho de banda máximo de memoria de 460 GB/s.

## 2. Subsistema de Almacenamiento y Expansión
- **Bahías Frontales**: 16 bahías U.3 NVMe PCIe 5.0 hot-swap configuradas en matriz RAID 10 por hardware mediante controladora Broadcom MegaRAID 9660-16i.
- **Rendimiento de E/S**: Velocidad sostenida de lectura secuencial de hasta 28,000 MB/s y escritura secuencial de 22,000 MB/s con 4.2 millones de IOPS aleatorios en bloques de 4K.
- **Ranuras PCIe**: 4 ranuras PCIe Gen 5 x16 de altura y longitud completas para aceleradores GPU (diseñadas para Nvidia H100 / L40S) y 2 ranuras OCP 3.0.

## 3. Interfaces de Red y Conectividad
- **Puertos Principales**: Tarjeta dual Mellanox ConnectX-7 con dos puertos QSFP112 que soportan velocidades de 400 GbE (Gigabit Ethernet) o InfiniBand NDR.
- **Puerto de Gestión Fuera de Banda (OOB)**: Puerto Ethernet RJ-45 dedicado de 1 GbE compatible con IPMI 2.0 y Redfish API versión 1.15.

## 4. Alimentación Eléctrica y Refrigeración
- **Fuentes de Poder**: Doble fuente redundante (1+1) de 2600W con certificación Titanium (eficiencia del 96% al 50% de carga). Voltaje de entrada admitido: 200V - 240V AC.
- **Disipación Térmica**: Sistema de refrigeración líquida directa al chip (DLC) con bucle cerrado para las CPUs y 6 ventiladores redundantes de 80 mm para el flujo de aire del chasis.
- **Rango Operativo de Temperatura**: De 10°C a 35°C con una humedad relativa sin condensación de 10% a 85%.
