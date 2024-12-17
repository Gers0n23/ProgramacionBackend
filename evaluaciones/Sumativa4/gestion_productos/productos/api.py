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
    description="API para gestionar productos, categorías y marcas",
    version="1.0.0"
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
    Obtiene un token de acceso JWT mediante credenciales
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
    Obtiene lista de todas las categorías disponibles
    """
    return Categoria.objects.all()

# Endpoints Marcas
@api.get("/marcas", response=List[MarcaOutSchema], tags=["Marcas"])
def listar_marcas(request):
    """
    Obtiene lista de todas las marcas disponibles
    """
    return Marca.objects.all()

# Agregar después de los otros schemas
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

# Agregar después de los otros endpoints
@api.get("/productos", response=List[ProductoBasicoSchema], tags=["Productos"])
def listar_productos(request, marca_id: Optional[int] = None, categoria_id: Optional[int] = None):
    """
    Obtiene lista de productos. Puede filtrarse por marca o categoría
    """
    productos = Producto.objects.select_related('marca', 'categoria')
    
    if marca_id is not None:
        marca = get_object_or_404(Marca, id=marca_id)
        productos = productos.filter(marca=marca)
    
    if categoria_id is not None:
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

@api.get("/productos/{codigo}", response={200: ProductoDetalleSchema, 404: dict}, tags=["Productos"])
def obtener_producto(request, codigo: str):
    """
    Obtiene el detalle de un producto por su código
    """
    producto = get_object_or_404(Producto, codigo=codigo)
    return producto

@api.patch("/productos/{codigo}", 
          auth=AuthBearer(),
          response={200: ProductoDetalleSchema, 404: dict, 400: dict}, 
          tags=["Productos"])
def actualizar_producto(request, codigo: str, datos: ProductoUpdateSchema):
    """
    Actualiza parcialmente un producto. Requiere autenticación.
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