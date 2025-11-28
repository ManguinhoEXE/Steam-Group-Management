# 🎮 Steam Group - Sistema de Compras Compartidas

API REST para gestionar compras compartidas de juegos de Steam entre un grupo de 6 personas, construida con FastAPI, PostgreSQL (Supabase) y almacenamiento de imágenes en Cloudinary.

## 🌐 Despliegue

La API está desplegada en [Render](https://render.com/).

## 🚀 Características

- ✅ Sistema de autenticación con JWT (HTTPOnly cookies)
- ✅ Gestión de depósitos y saldo de usuarios
- ✅ Sistema de propuestas de juegos
- ✅ Sistema de votación con voto único
- ✅ Compras compartidas con split 40/60
- ✅ Control absoluto del Master
- ✅ Base de datos PostgreSQL (Supabase)
- ✅ Almacenamiento de imágenes de perfil en Cloudinary
- ✅ Documentación automática (Swagger/ReDoc)

## 📋 Requisitos

- Python 3.11+
- PostgreSQL (Supabase)
- pip

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd Steam
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno


Edita `.env` con tu información de Supabase, JWT y Cloudinary (ejemplo):

```env
# Base de datos Supabase
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/db

# Supabase Auth
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=tu_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_supabase_service_role_key

# JWT
JWT_SECRET_KEY=tu_clave_secreta
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Cookies
COOKIE_DOMAIN=localhost
COOKIE_SECURE=false
COOKIE_SAMESITE=lax

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
CLOUDINARY_URL=cloudinary://tu_api_key:tu_api_secret@tu_cloud_name
```
## 🖼️ Gestión de imágenes de perfil con Cloudinary

- Las imágenes de perfil se suben a Cloudinary mediante el endpoint `/auth/upload-profile-image`.
- Al subir una imagen:
  - Se almacena la URL de la imagen principal (500x500) en el campo `profile_image` del usuario en la base de datos.
  - Cloudinary genera automáticamente versiones optimizadas:
    - `profile_image`: 500x500 (principal)
    - `url_thumbnail`: 200x200 (listas)
    - `url_small`: 100x100 (avatar)
- Todas las URLs son públicas, permanentes y servidas por CDN global.
- Al eliminar la imagen de perfil, también se elimina de Cloudinary y se borra la referencia en la base de datos.

**Impacto:**  
No se almacena la imagen en el servidor ni en la base de datos, solo la URL segura proporcionada por Cloudinary.

---

## 🔐 Recuperación de contraseña

1. El usuario solicita recuperación con su email vía `/auth/password-reset-request`.
2. El backend usa Supabase para enviar un correo con un enlace de reseteo.
3. El usuario sigue el enlace y cambia la contraseña desde el frontend (usando el SDK de Supabase).
4. No se expone endpoint para cambiar la contraseña directamente desde el backend.

---

## 🧪 Pruebas automatizadas

- El proyecto incluye pruebas automatizadas con **pytest**.
- Las pruebas cubren los principales flujos de la API: registro, login, depósitos, propuestas, votaciones, compras, etc.
- Se ejecutan con:
  ```bash
  python -m pytest tests/
  ```
- Permiten validar que la API funciona correctamente y que los endpoints cumplen las reglas de negocio.

---

## 🎮 Ejecutar la aplicación

### Opción 1: Con uvicorn directamente
```bash
uvicorn main:app --reload
```

### Opción 2: Con el script run.py
```bash
python run.py
```

La API estará disponible en: http://localhost:8000

## 📚 Documentación

FastAPI genera documentación automática e interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 SISTEMA DE USUARIOS Y ROLES

### Estructura del grupo (6 personas):
- **1 Master**: Control absoluto del sistema
- **5 Usuarios normales**: Pueden proponer, votar y participar en compras

### 👑 Privilegios del Master

**PUEDE hacer:**
- ✅ Crear depósitos para usuarios
- ✅ Comprar juegos aprobados
- ✅ Ver saldos y estadísticas de todos
---

## 🛠️ ENDPOINTS PRINCIPALES

### 🔐 Autenticación (`/auth`)

#### Registrar usuario
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "username": "Juan"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Logout
```http
POST /auth/logout
```

#### Usuario actual
```http
GET /auth/me
```

---

### 💰 Depósitos (`/deposits`)

#### Crear depósito (solo Master)
```http
POST /deposits/
Authorization: Bearer <token_master>
Content-Type: application/json

{
  "user_id": 2,
  "amount": 50000
}
```

#### Ver mi saldo
```http
GET /deposits/my-balance
Authorization: Bearer <token>
```

#### Ver todos los saldos (solo Master)
```http
GET /deposits/balances
Authorization: Bearer <token_master>
```

---

### 🎮 Propuestas (`/proposals`)

#### Crear propuesta
```http
POST /proposals/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Red Dead Redemption 2",
  "price": 100000
}
```

**Reglas:**
- ✅ Todos pueden proponer (incluyendo Master)
- ✅ Solo una propuesta activa por usuario

#### Ver todas las propuestas
```http
GET /proposals/
```

#### Votar propuesta
```http
POST /proposals/{proposal_id}/vote
Authorization: Bearer <token>
```

**Reglas de votación:**
- ❌ No puedes votar tu propia propuesta
- ✅ Solo UN voto activo a la vez
- ✅ Si votas otra propuesta, se elimina automáticamente tu voto anterior

#### Ver mi voto actual
```http
GET /proposals/my-vote
Authorization: Bearer <token>
```

#### Seleccionar ganador (solo Master)
```http
POST /proposals/{proposal_id}/select-winner
Authorization: Bearer <token_master>
```

**Efecto:**
- ✅ La propuesta seleccionada pasa a estado 'approved'
- ✅ Todas las demás propuestas se rechazan automáticamente

---

### 🛒 Compras (`/purchases`)

#### Comprar desde propuesta aprobada (solo Master)
```http
POST /purchases/from-proposal/{proposal_id}
Authorization: Bearer <token_master>
Content-Type: application/json

{
  "was_on_sale": true,
  "original_price": 100000
}
```

**Parámetros:**
- `was_on_sale` (bool, opcional): Si el juego estaba en oferta (default: false)
- `original_price` (int, opcional): Precio original antes de descuento (default: null)

**Split de pago automático:**
- **Propietario (quien propuso)**: Paga 40% del precio
- **Otros 5 usuarios**: Pagan 12% cada uno (60% total / 5)

**Ejemplo:**
Juego de $100,000:
- Propietario: $40,000
- Otros 5: $12,000 cada uno

#### Compra manual (solo Master)
```http
POST /purchases/?owner_id={user_id}
Authorization: Bearer <token_master>
Content-Type: application/json

{
  "title": "Cyberpunk 2077",
  "total_price": 80000,
  "was_on_sale": false
}
```

#### Ver mis compras
```http
GET /purchases/my-purchases
Authorization: Bearer <token>
```

#### Ver todas las participaciones
```http
GET /purchases/my-participations
Authorization: Bearer <token>
```

---

## 🎯 FLUJO COMPLETO DE COMPRA

### Escenario: Comprar Red Dead Redemption 2

1. **Usuario propone juego**
```http
POST /proposals/
{
  "title": "Red Dead Redemption 2",
  "price": 50000
}
```

2. **Otros usuarios votan**
```http
POST /proposals/1/vote
```

3. **Master selecciona ganador**
```http
POST /proposals/1/select-winner
```

4. **Master compra el juego**

**Opción A - Precio normal:**
```http
POST /purchases/from-proposal/1
{
  "was_on_sale": false
}
```

**Opción B - En oferta:**
```http
POST /purchases/from-proposal/1
{
  "was_on_sale": true,
  "original_price": 100000
}
```

**Resultado:**
- ✅ Propietario paga $20,000 (40%)
- ✅ Otros 5 pagan $6,000 cada uno (12%)
- ✅ Saldos se descuentan automáticamente
- ✅ Se crean 6 registros en `purchase_shares`

---

## 📊 EJEMPLOS DE USO

### Ejemplo 1: Votación con cambio de voto

**Pedro vota Red Dead:**
```http
POST /proposals/1/vote
```
Respuesta:
```json
{
  "message": "Voto registrado exitosamente",
  "vote": {
    "proposal_id": 1,
    "proposal_title": "Red Dead Redemption 2",
    "current_votes": 1
  }
}
```

**Pedro cambia su voto a GTA V:**
```http
POST /proposals/2/vote
```
Respuesta:
```json
{
  "message": "Voto cambiado exitosamente",
  "vote": {
    "proposal_id": 2,
    "proposal_title": "GTA V",
    "current_votes": 1
  },
  "previous_vote": {
    "proposal_title": "Red Dead Redemption 2",
    "message": "Tu voto anterior en 'Red Dead Redemption 2' ha sido eliminado"
  }
}
```

---

### Ejemplo 2: Master selecciona ganador

**Escenario:**
- Red Dead: 3 votos
- GTA V: 1 voto
- FIFA 24: 0 votos

**Master decide comprar FIFA 24:**
```http
POST /proposals/3/select-winner
```

**Resultado:**
- ✅ FIFA 24 → `approved`
- ❌ Red Dead → `rejected`
- ❌ GTA V → `rejected`

---

## 📦 Estructura del proyecto

```
Steam/
├── app/
│   ├── __init__.py
│   ├── database.py             # Configuración de conexión a Supabase
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # Modelos SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Schemas Pydantic
│   │   └── auth_schemas.py     # Schemas de autenticación
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth_router.py      # Endpoints de autenticación
│   │   ├── deposits_router.py  # Endpoints de depósitos
│   │   ├── proposals_router.py # Endpoints de propuestas
│   │   └── purchases_router.py # Endpoints de compras
│   └── utils/
│       ├── __init__.py
│       └── auth.py             # Utilidades JWT y autenticación
├── main.py                     # Aplicación principal FastAPI
├── requirements.txt            # Dependencias del proyecto
├── .env                        # Variables de entorno (NO subir a git)
├── .gitignore                  # Archivos ignorados por git
└── README.md                   # Documentación (este archivo)
```

---

## 🗄️ MODELO DE BASE DE DATOS

El sistema utiliza PostgreSQL (Supabase) y está compuesto por las siguientes tablas principales:

### steamuser
| Campo         | Tipo        | Descripción                       |
|-------------- |------------ |-----------------------------------|
| id            | int8        | Identificador único                |
| name          | text        | Nombre de usuario                  |
| created_at    | timestamptz | Fecha de creación                  |
| updated_at    | timestamptz | Fecha de última actualización      |
| role          | text        | Rol (master/user)                  |
| auth_uid      | uuid        | UID de autenticación Supabase      |
| active        | bool        | Usuario activo/inactivo            |
| profile_image | text        | URL de imagen de perfil (Cloudinary)|

### game_proposals
| Campo           | Tipo        | Descripción                       |
|---------------- |------------ |-----------------------------------|
| id              | int8        | Identificador único                |
| title           | text        | Título de la propuesta             |
| proposer_id     | int8        | ID del usuario que propone         |
| price           | int4        | Precio propuesto                   |
| proposed_at     | timestamptz | Fecha de propuesta                 |
| status          | text        | Estado de la propuesta             |
| proposal_number | int4        | Número de propuesta                |
| month_year      | int4        | Mes y año de la propuesta          |

### purchases
| Campo         | Tipo        | Descripción                       |
|-------------- |------------ |-----------------------------------|
| id            | int8        | Identificador único                |
| proposal_id   | int8        | ID de la propuesta asociada        |
| title         | text        | Título del juego comprado          |
| total_price   | int4        | Precio total de la compra          |
| purchaser_id  | int8        | ID del usuario que realiza la compra|
| purchased_at  | timestamptz | Fecha de compra                    |
| was_on_sale   | bool        | ¿Estaba en oferta?                 |
| original_price| int4        | Precio original (sin descuento)    |
| owner_id      | int8        | ID del usuario propietario         |

### deposits
| Campo      | Tipo        | Descripción                       |
|----------- |------------ |-----------------------------------|
| id         | int8        | Identificador único                |
| member_id  | int8        | ID del usuario                     |
| amount     | int4        | Monto del depósito                 |
| note       | text        | Nota adicional                     |
| date       | timestamptz | Fecha del depósito                 |
| created_at | timestamptz | Fecha de registro                  |

### purchase_shares
| Campo        | Tipo        | Descripción                       |
|------------- |------------ |-----------------------------------|
| id           | int8        | Identificador único                |
| purchase_id  | int8        | ID de la compra asociada           |
| member_id    | int8        | ID del usuario                     |
| share_amount | int4        | Monto de la participación          |
| paid         | bool        | ¿Pagado?                           |
| paid_at      | timestamptz | Fecha de pago                      |
| created_at   | timestamptz | Fecha de registro                  |

### votes
| Campo       | Tipo        | Descripción                       |
|------------ |------------ |-----------------------------------|
| id          | int8        | Identificador único                |
| proposal_id | int8        | ID de la propuesta                 |
| member_id   | int8        | ID del usuario                     |
| vote        | bool        | Voto (aprobado/rechazado)          |
| voted_at    | timestamptz | Fecha del voto                     |

### proposals_turn
| Campo  | Tipo | Descripción                |
|--------|------|----------------------------|
| id     | int8 | Identificador único        |
| status | bool | Estado del turno de propuestas |

#### Relaciones principales
- **steamuser** se relaciona con depósitos, propuestas, compras, votos y participaciones.
- **game_proposals** puede ser votada y convertirse en una compra.
- **purchases** se divide entre usuarios mediante **purchase_shares**.
- **votes** vincula usuarios y propuestas.
- **deposits** registra los movimientos de saldo de cada usuario.

---

## 🔐 Seguridad

- **JWT con HTTPOnly cookies**: Protección contra XSS
- **Supabase Auth**: Gestión de usuarios integrada
- **NUNCA** subas el archivo `.env` a control de versiones
- En producción, configura CORS apropiadamente

---

## ⚙️ Variables de Entorno

```env
# Supabase Database (Session Pooler)
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Supabase Config
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=tu_supabase_anon_key

# JWT
JWT_SECRET_KEY=tu_secret_key_super_segura_aqui
```

---

## 🧪 PRUEBAS RÁPIDAS

### 1. Registrar usuarios de prueba

```bash
# Registrar Master
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "master@steam.com", "password": "master123", "username": "Master"}'

# Registrar Usuario 1
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "juan@steam.com", "password": "juan123", "username": "Juan"}'
```

### 2. Login y obtener token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "master@steam.com", "password": "master123"}'
```

### 3. Crear depósito

```bash
curl -X POST "http://localhost:8000/deposits/" \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "amount": 100000}'
```

### 4. Proponer juego

```bash
curl -X POST "http://localhost:8000/proposals/" \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Red Dead Redemption 2", "price": 50000}'
```

---

## 💡 REGLAS DE NEGOCIO

### Sistema de Split de Pagos (40/60)
- **Propietario**: Paga 40% del precio total
- **Otros 5 usuarios**: Pagan 12% cada uno (60% / 5)
- **Ejemplo** - Juego de $100,000:
  - Propietario: $40,000
  - Usuario 2-6: $12,000 cada uno

### Votación
- Cada usuario tiene **UN solo voto activo**
- Cambiar voto **elimina automáticamente** el voto anterior
- Master **NO vota** (solo decide ganador)
- No puedes votar tu propia propuesta

### Propuestas
- Todos pueden proponer (incluyendo Master)
- Solo **una propuesta activa** por usuario
- Master selecciona ganador **manualmente** (sin importar votos)
- Al seleccionar ganador, las demás propuestas se **rechazan automáticamente**

### Compras
- Solo Master puede ejecutar compras
- Saldos se **descuentan automáticamente**
- Se crean 6 participaciones (1 propietario + 5 usuarios)
- Se puede registrar si fue compra en oferta

---

## 🚀 ROADMAP

- [x] Sistema de autenticación JWT
- [x] Sistema de depósitos
- [x] Sistema de propuestas
- [x] Sistema de votación con voto único
- [x] Sistema de compras compartidas 40/60
- [x] Control de Master
- [x] Registro de ofertas en compras
- [x] Dashboard de estadísticas
- [x] Historial de transacciones
- [ ] Sistema de notificaciones
- [ ] Tests unitarios
- [ ] Dockerizar aplicación

---

## 📖 Recursos

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación Supabase](https://supabase.com/docs)
- [Pydantic](https://docs.pydantic.dev/)

## 👤 Autor

**ManguinhoEXE**

---

## 🎮 ¡Disfruta tu biblioteca compartida de Steam!
