from ninja import NinjaAPI, Schema
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from jose import jwt
from datetime import datetime, timedelta
from typing import List, Optional
from .models import Producto, Categoria, Marca
from django.conf import settings
from django.shortcuts import get_object_or_404
from http import HTTPStatus

# Configuración de la API con documentación
api = NinjaAPI(
    title="API Gestión de Productos",
    version="1.0.0",
    description="""
    API REST para la gestión de productos del Supermercado Ketim Porta.
    
    ## Características
    * Gestión de productos, categorías y marcas
    * Autenticación mediante JWT
    * Filtrado de productos por marca o categoría
    
    ## Autenticación
    Para usar los endpoints protegidos:
    1. Obtener token JWT vía /api/auth/token
    2. Incluir en headers: `Authorization: Bearer <token>`
    
    ## Ejemplos de Uso
    Obtener token:
    ```
    POST /api/auth/token
    {
        "username": "usuario",
        "password": "contraseña"
    }
    ```
    """
)

# Manejo de errores
class Error404(Exception):
    pass

class ValidationError(Exception):
    pass

@api.exception_handler(Error404)
def not_found(request, exc):
    return api.create_response(request, {"mensaje": "Recurso no encontrado"}, status=404)

@api.exception_handler(ValidationError)
def validation_error(request, exc):
    return api.create_response(request, {"mensaje": str(exc)}, status=422)

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            print(f"Token recibido: {token}")  # Debug
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            print(f"Payload: {payload}")  # Debug
            return payload
        except Exception as e:
            print(f"Error de autenticación: {str(e)}")  # Debug
            return None

# Schemas
class TokenSchema(Schema):
    username: str
    password: str

class TokenOutSchema(Schema):
    access_token: str
    token_type: str = "bearer"

class CategoriaOutSchema(Schema):
    id: int
    nombre: str

class MarcaOutSchema(Schema):
    id: int
    nombre: str

# Auth endpoints
@api.post("/auth/token", response={
    200: TokenOutSchema,
    401: dict
}, tags=["Autenticación"])
def get_token(request, credentials: TokenSchema):
    """
    Obtiene un token JWT para autenticación.
    
    Args:
        credentials: Credenciales de usuario (username y password)
    
    Returns:
        200: Token JWT válido
        401: Credenciales inválidas
    
    Ejemplo:
        ```json
        {
            "username": "admin",
            "password": "inacap2024"
        }
        ```
    """
    user = authenticate(username=credentials.username, password=credentials.password)
    if user is None:
        return 401, {"mensaje": "Credenciales inválidas"}
    
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return 200, {"access_token": token, "token_type": "bearer"}

# Endpoints Categorías
@api.get("/categorias", response=List[CategoriaOutSchema], tags=["Categorías"])
def listar_categorias(request):
    """
    Lista todas las categorías disponibles.
    
    Returns:
        200: Lista de categorías
        
    Ejemplo respuesta:
        ```json
        [
            {
                "id": 1,
                "nombre": "Electrónicos"
            },
            {
                "id": 2,
                "nombre": "Alimentos"
            }
        ]
        ```
    """
    return Categoria.objects.all()

# Endpoints Marcas
@api.get("/marcas", response=List[MarcaOutSchema], tags=["Marcas"])
def listar_marcas(request):
    """
    Lista todas las marcas disponibles.
    
    Returns:
        200: Lista de marcas
        
    Ejemplo respuesta:
        ```json
        [
            {
                "id": 1,
                "nombre": "Samsung"
            },
            {
                "id": 2,
                "nombre": "LG"
            }
        ]
        ```
    """
    return Marca.objects.all()


class ProductoBasicoSchema(Schema):
    codigo: str
    nombre: str
    precio: float
    marca_id: int
    marca_nombre: str

    @staticmethod
    def resolve_marca(obj):
        return obj.marca.nombre if obj.marca else None

class ProductoDetalleSchema(Schema):
    codigo: str
    nombre: str
    precio: float
    marca_id: int
    marca_nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    caracteristicas: Optional[List[str]] = []
    fecha_vencimiento: Optional[str] = None

class ProductoUpdateSchema(Schema):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    marca_id: Optional[int] = None
    categoria_id: Optional[int] = None
    
class ProductoUpdateCompletoSchema(Schema):
    nombre: str
    precio: float
    marca_id: int
    categoria_id: int
    caracteristicas: List[int]
    fecha_vencimiento: str


@api.get("/productos", response=List[ProductoBasicoSchema], tags=["Productos"])
def listar_productos(request, marca_id: Optional[int] = None, categoria_id: Optional[int] = None):
    """
    Lista productos con filtrado opcional por marca O categoría.
    
    Args:
        marca_id: ID de marca para filtrar (opcional)
        categoria_id: ID de categoría para filtrar (opcional)
        
    Notas:
        - Solo se puede filtrar por marca O categoría, no ambos
        - Si no se especifica filtro, retorna todos los productos
    
    Returns:
        200: Lista de productos
        422: Error de validación (si se usan ambos filtros)
    """
    if marca_id is not None and categoria_id is not None:
        raise ValidationError("Solo se puede filtrar por marca O por categoría, no ambos")
    
    productos = Producto.objects.select_related('marca', 'categoria')
    
    if marca_id is not None:
        marca = get_object_or_404(Marca, id=marca_id)
        productos = productos.filter(marca=marca)
    elif categoria_id is not None:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        productos = productos.filter(categoria=categoria)

    return [
        {
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "marca_id": producto.marca.id,
            "marca_nombre": producto.marca.nombre
        } 
        for producto in productos
    ]


@api.patch("/productos/{codigo}", 
          auth=AuthBearer(),
          response={200: ProductoDetalleSchema, 404: dict, 400: dict}, 
          tags=["Productos"])
def actualizar_producto(request, codigo: str, datos: ProductoUpdateSchema):
    """
    Actualiza parcialmente un producto. Requiere autenticación JWT.
    
    Args:
        codigo: Código único del producto
        datos: Campos a actualizar (opcionales)
    
    Requerimientos:
        - Token JWT válido en header Authorization
        - Al menos un campo para actualizar
    
    Ejemplo:
        ```json
        {
            "precio": 1999.99,
            "nombre": "Nuevo Nombre"
        }
        ```
    
    Returns:
        200: Producto actualizado
        400: Error en datos enviados
        401: No autorizado
        404: Producto no encontrado
    """
    try:
        producto = get_object_or_404(Producto, codigo=codigo)
        datos_dict = datos.dict(exclude_unset=True)
        
        for field, value in datos_dict.items():
            setattr(producto, field, value)
        
        producto.save()
        
        # Construir respuesta completa
        return {
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "marca_id": producto.marca.id if producto.marca else None,
            "marca_nombre": producto.marca.nombre if producto.marca else None,
            "categoria_id": producto.categoria.id if producto.categoria else None,
            "caracteristicas": [c.nombre for c in producto.caracteristicas.all()],
            "fecha_vencimiento": producto.fecha_vencimiento.isoformat() if producto.fecha_vencimiento else None
        }
    except Exception as e:
        print(f"Error al actualizar: {str(e)}")
        return api.create_response(
            request,
            {"detail": str(e)},
            status=400
        )

@api.put("/productos/{codigo}", 
         auth=AuthBearer(),
         response={200: ProductoDetalleSchema, 404: dict, 400: dict}, 
         tags=["Productos"])
def actualizar_producto_completo(request, codigo: str, datos: ProductoUpdateCompletoSchema):
    """
    Actualiza TODOS los campos de un producto. Requiere autenticación JWT.
    
    Args:
        codigo: Código único del producto
        datos: Todos los datos del producto (requeridos)
    
    Requerimientos:
        - Token JWT válido en header Authorization
        - Todos los campos son obligatorios
    
    Ejemplo:
        ```json
        {
            "nombre": "Producto Nuevo",
            "precio": 1999.99,
            "marca_id": 1,
            "categoria_id": 1,
            "caracteristicas": [1, 2],
            "fecha_vencimiento": "2024-12-31"
        }
        ```
    
    Returns:
        200: Producto actualizado
        400: Error en datos enviados
        401: No autorizado
        404: Producto no encontrado
    """
    try:
        producto = get_object_or_404(Producto, codigo=codigo)
        
        # Validar marca y categoría
        marca = get_object_or_404(Marca, id=datos.marca_id)
        categoria = get_object_or_404(Categoria, id=datos.categoria_id)
        
        # Actualizar todos los campos
        producto.nombre = datos.nombre
        producto.precio = datos.precio
        producto.marca = marca
        producto.categoria = categoria
        producto.fecha_vencimiento = datetime.strptime(datos.fecha_vencimiento, '%Y-%m-%d').date()
        
        # Actualizar características
        producto.caracteristicas.clear()
        producto.caracteristicas.set(datos.caracteristicas)
        
        producto.save()
        
        return {
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "marca_id": producto.marca.id,
            "marca_nombre": producto.marca.nombre,
            "categoria_id": producto.categoria.id,
            "caracteristicas": [c.nombre for c in producto.caracteristicas.all()],
            "fecha_vencimiento": producto.fecha_vencimiento.isoformat()
        }
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=400
        )