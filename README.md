# 🎮 Steam Group - Sistema de Compras Compartidas

API REST para gestionar compras compartidas de juegos de Steam entre un grupo de 6 personas, construida con FastAPI y PostgreSQL (Supabase).

## 🚀 Características

- ✅ Sistema de autenticación con JWT (HTTPOnly cookies)
- ✅ Gestión de depósitos y saldo de usuarios
- ✅ Sistema de propuestas de juegos
- ✅ Sistema de votación con voto único
- ✅ Compras compartidas con split 40/60
- ✅ Control absoluto del Master
- ✅ Base de datos PostgreSQL (Supabase)
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

### 2. Crear entorno virtual

```bash
python -m venv venv

# Activar en Windows
.\venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Edita `.env` con tu información de Supabase:

```env
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=tu_supabase_anon_key
JWT_SECRET_KEY=tu_secret_key_aqui
```

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

---

## 🎯 SISTEMA DE USUARIOS Y ROLES

### Estructura del grupo (6 personas):
- **1 Master**: Control absoluto del sistema
- **5 Usuarios normales**: Pueden proponer, votar y participar en compras

### 👑 Privilegios del Master

**PUEDE hacer:**
- ✅ Proponer juegos (como cualquier usuario)
- ✅ Seleccionar ganador manualmente (sin importar votos)
- ✅ Crear depósitos para usuarios
- ✅ Comprar juegos aprobados
- ✅ Ver saldos y estadísticas de todos

**NO PUEDE hacer:**
- ❌ Votar en propuestas (solo decide el ganador)

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
- ❌ Master NO puede votar
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

## �️ MODELOS DE BASE DE DATOS

### User
- `id`, `email`, `username`, `password_hash`, `is_master`, `balance`, `supabase_id`

### Deposit
- `id`, `user_id`, `amount`, `created_at`

### GameProposal
- `id`, `user_id`, `title`, `price`, `status` (proposed/approved/rejected), `created_at`

### Vote
- `id`, `user_id`, `proposal_id`, `created_at`

### Purchase
- `id`, `title`, `total_price`, `owner_id`, `proposal_id`, `was_on_sale`, `original_price`, `created_at`

### PurchaseShare
- `id`, `purchase_id`, `user_id`, `share_amount`, `created_at`

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
- [ ] Dashboard de estadísticas
- [ ] Historial de transacciones
- [ ] Sistema de notificaciones
- [ ] Tests unitarios
- [ ] Dockerizar aplicación

---

## 📖 Recursos

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación Supabase](https://supabase.com/docs)
- [Pydantic](https://docs.pydantic.dev/)

---

## 📝 Licencia

MIT

---

## 👤 Autor

**ManguinhoEXE**

---

## 🎮 ¡Disfruta tu biblioteca compartida de Steam!
