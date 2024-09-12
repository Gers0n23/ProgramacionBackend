# Gestión de Productos

## Descripción
Este proyecto es una aplicación web desarrollada con Django para la empresa ficticia "Gestión de Productos S.A.". Permite a los administradores registrar y consultar datos básicos de los productos de la empresa.

## Características
- Registro de productos con los siguientes datos:
  - Código
  - Nombre
  - Marca
  - Fecha de vencimiento
- Almacenamiento temporal de datos en memoria durante la ejecución del servidor
- Consulta de la lista de productos registrados
- Interfaz de usuario estilizada con CSS moderno

## Requisitos
- Python 3.8+
- Django 5.1+

## Instalación
1. Clona este repositorio:

git clone [https://github.com/tu-usuario/gestion-productos.git](https://github.com/tu-usuario/gestion-productos.git)
cd gestion-productos

2. Crea un entorno virtual y actívalo:

python -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`

3. Instala las dependencias:

pip install -r requirements.txt

4. Realiza las migraciones:

python manage.py makemigrations
python manage.py migrate

## Uso
1. Inicia el servidor de desarrollo:

python manage.py runserver

2. Abre tu navegador y visita `http://localhost:8000`

3. Utiliza la interfaz para registrar nuevos productos y consultar la lista de productos existentes.

## Estructura del Proyecto

gestion_productos/
├── gestion_productos/
│   ├── **init**.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── productos/
│   ├── **init**.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── base.html
│   ├── registro.html
│   └── consulta.html
├── manage.py
└── README.md

## Desarrollo
- El proyecto está desarrollado utilizando Django como framework web.
- Se utiliza SQLite como base de datos por defecto.
- Los estilos están definidos en `static/css/styles.css`.
- Las plantillas HTML se encuentran en el directorio `templates/`.

## Contribuir
Si deseas contribuir al proyecto, por favor:
1. Haz un fork del repositorio
2. Crea una nueva rama para tu función: `git checkout -b nueva-funcion`
3. Realiza tus cambios y haz commit: `git commit -am 'Añade nueva función'`
4. Haz push a la rama: `git push origin nueva-funcion`
5. Envía un pull request

## Contacto
Si tienes alguna pregunta o sugerencia, no dudes en contactarme en [gerson.cordero@inacapmail.cl].