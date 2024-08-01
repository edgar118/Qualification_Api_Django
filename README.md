<h1 align="center" id="title">Gestión Académica</h1>

<p id="description">Este proyecto es una aplicación web para la gestión académica desarrollada con Django y Django REST Framework. Permite la gestión de estudiantes profesores materias e inscripciones. Proporciona una API para realizar diversas operaciones como inscribir estudiantes en materias consultar calificaciones y gestionar la asignación de materias a los profesores.</p>

  
  
<h2>🧐 Features</h2>

Here're some of the project's best features:

*   Documentación de la API La documentación de la API se puede acceder en http://localhost:8000/swagger/ después de levantar los contenedores.

<h2>🛠️ Installation Steps:</h2>

<p>1. Clonar el repositorio:</p>

```
git clone https://github.com/tu-usuario/tu-repositorio.git cd tu-repositorio
```

<p>2. Construir y ejecutar los contenedores con Docker Compose:</p>

```
docker-compose up --build
```

<p>3. Acceder a la aplicación en el navegador en http://localhost:8000</p>

  
  
<h2>💻 Built with</h2>

Technologies used in the project:

*   Backend: Django Django REST Framework
*   Base de Datos: SQLite (por defecto) se puede configurar para usar PostgreSQL
*   Autenticación: JSON Web Tokens (JWT)
*   Docker: Docker y Docker Compose para la contenedorización de la aplicación
