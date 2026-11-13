# Estándar de Seguridad en Desarrollo de Software (SSDLC)

## 1. Criptografía y Gestión de Secretos
- **Algoritmos Autorizados**:
  - Para datos en reposo: Cifrado simétrico AES-256 en modo GCM (Galois/Counter Mode). Queda estrictamente prohibido el uso de AES-ECB o DES/3DES.
  - Para firma digital y llaves asimétricas: Curvas elípticas Ed25519 o RSA con llaves mínimas de 3072 bits.
  - Para funciones hash de contraseñas: Argon2id (parámetros recomendados: memoria 64 MB, 3 iteraciones, 4 hilos) o bcrypt con factor de coste mínimo de 12. Prohibido SHA-1 y MD5.
- **Gestión de Credenciales**:
  - Cero secretos en código fuente: Ninguna API Key, token o contraseña debe alojarse en repositorios Git.
  - Uso obligatorio de Vault (HashiCorp) o AWS Secrets Manager con rotación automática de credenciales cada 90 días.

## 2. Validación de Entradas y Prevención de Inyecciones
- **Consultas a Base de Datos**: Uso obligatorio de ORM con consultas parametrizadas o sentencias preparadas (Prepared Statements). Queda prohibida la concatenación directa de cadenas SQL.
- **Sanitización de Salidas (Prevención XSS)**: Todo texto renderizado en clientes web o móviles debe ser escapado contextualmente según HTML, JavaScript o CSS. Uso obligatorio de Content Security Policy (CSP) nivel 3.
- **Prevención de SSRF**: Toda petición HTTP saliente originada por peticiones de usuarios debe validar la URL de destino contra una lista blanca estricta y bloquear rangos privados (RFC 1918, RFC 3927 y localhost 127.0.0.1).

## 3. Pipeline CI/CD y Análisis Estático
- Todo Pull Request debe superar satisfactoriamente:
  - Análisis Estático de Seguridad de Código (SAST) con SonarQube (sin vulnerabilidades bloqueantes o críticas).
  - Análisis de Composición de Software (SCA) con Snyk o Trivy para detectar dependencias con CVEs conocidos con severidad CVSS superior a 7.0.
  - Cobertura de pruebas unitarias mínima del 80% sobre líneas de código de lógica de negocio.
