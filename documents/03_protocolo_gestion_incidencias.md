# Protocolo Operativo: Clasificación y Gestión de Incidencias Críticas (ITIL v4)

## 1. Niveles de Severidad y Tiempos de Respuesta (SLA)
- **Severidad 1 (Crítica / Bloqueante)**:
  - *Definición*: Caída total de servicios de producción, pérdida de ingresos en tiempo real o brecha de seguridad con compromiso de datos.
  - *Tiempo de Respuesta Inicial*: Menos de 15 minutos.
  - *Tiempo Máximo de Mitigación (MTTR)*: 2 horas.
  - *Canal de Comunicación*: Activación de puente de audio de emergencia en Slack `#war-room-p1` y notificación vía PagerDuty a líderes de ingeniería.
- **Severidad 2 (Alta)**:
  - *Definición*: Degradación importante del rendimiento del sistema, fallo en transacciones no críticas o falla parcial con workaround disponible.
  - *Tiempo de Respuesta*: Menos de 45 minutos.
  - *Tiempo de Mitigación*: 6 horas.
- **Severidad 3 (Media/Baja)**:
  - *Definición*: Errores cosméticos, bugs en paneles administrativos internos o solicitudes de servicio estándar.
  - *Tiempo de Respuesta*: 24 horas hábiles.
  - *Tiempo de Resolución*: Próximo sprint o 5 días hábiles.

## 2. Ruta de Escalamiento Técnico
1. **Primer Nivel (L1 - NOC / Helpdesk)**: Monitoreo con Datadog/Grafana, triage inicial, verificación de estado de salud (health checks) y reinicio automatizado de pods en Kubernetes.
2. **Segundo Nivel (L2 - SysAdmin / DevOps)**: Análisis de trazas de logs con Loki/ELK, inspección de cuellos de botella de red y escalado vertical/horizontal de recursos.
3. **Tercer Nivel (L3 - Core Engineering / DBA)**: Corrección de código fuente (hotfix), rollback de despliegues mediante ArgoCD y manipulación directa de bases de datos relacionales en modo de mantenimiento.

## 3. Proceso Post-Mortem Obligatorio
- Todo incidente clasificado como Severidad 1 o 2 requiere un informe Post-Mortem sin culpas ("Blameless Post-Mortem") entregado en un máximo de 72 horas hábiles.
- El documento debe incluir: línea temporal precisa del incidente en UTC, causa raíz (análisis de los 5 Porqués), impacto cuantitativo y plan de acciones correctivas preventivas (CAPA) con responsables asignados en Jira.
