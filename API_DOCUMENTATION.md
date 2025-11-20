# 📚 Documentación Completa de la API - Steam Group Management

**Base URL:** `http://localhost:8000`  
**Versión:** 1.0.0

---

## 📑 Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Depósitos](#depósitos)
3. [Propuestas](#propuestas)
4. [Compras](#compras)
5. [Códigos de Estado HTTP](#códigos-de-estado-http)
6. [Modelos de Datos](#modelos-de-datos)

---

## 🔐 Autenticación

### 1. Registrar Usuario

**Endpoint:** `POST /auth/register`  
**Autenticación:** No requerida  
**Descripción:** Registra un nuevo usuario en el sistema

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "name": "Nombre Usuario",
  "role": "steam"  // Opcional: "steam" (default) o "master"
}
```

**Response (201 Created):**
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "name": "Nombre Usuario",
    "role": "steam",
    "email": "usuario@ejemplo.com"
  }
}
```

**Cookies establecidas:**
- `steam_access_token` (HTTPOnly)
- `steam_refresh_token` (HTTPOnly)

---

### 2. Iniciar Sesión

**Endpoint:** `POST /auth/login`  
**Autenticación:** No requerida  
**Descripción:** Inicia sesión con email y password

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Inicio de sesión exitoso",
  "user": {
    "id": 1,
    "name": "Nombre Usuario",
    "role": "steam",
    "email": "usuario@ejemplo.com"
  }
}
```

**Cookies establecidas:**
- `steam_access_token` (HTTPOnly)
- `steam_refresh_token` (HTTPOnly)

---

### 3. Cerrar Sesión

**Endpoint:** `POST /auth/logout`  
**Autenticación:** Requerida  
**Descripción:** Cierra la sesión del usuario actual

**Response (200 OK):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

---

### 4. Obtener Usuario Actual

**Endpoint:** `GET /auth/me`  
**Autenticación:** Requerida  
**Descripción:** Obtiene la información del usuario autenticado

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Nombre Usuario",
  "role": "steam",
  "active": true,
  "profile_image": "uploads/profiles/1_abc12345.jpg",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-02T10:30:00Z",
  "auth_uid": "uuid-string-here"
}
```

---

### 5. Verificar Autenticación

**Endpoint:** `GET /auth/verify`  
**Autenticación:** Requerida  
**Descripción:** Verifica si el token es válido

**Response (200 OK):**
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "name": "Nombre Usuario",
    "role": "steam"
  }
}
```

---

### 6. Refrescar Token

**Endpoint:** `POST /auth/refresh`  
**Autenticación:** Refresh token requerido (cookie)  
**Descripción:** Obtiene un nuevo access token usando el refresh token

**Response (200 OK):**
```json
{
  "message": "Tokens refrescados exitosamente"
}
```

---

### 7. Subir Imagen de Perfil

**Endpoint:** `POST /auth/upload-profile-image`  
**Autenticación:** Requerida  
**Content-Type:** `multipart/form-data`  
**Descripción:** Sube o actualiza la imagen de perfil del usuario en Cloudinary

**Request Body (form-data):**
- `file`: Archivo de imagen (JPG, PNG, WebP, GIF)

**Validaciones:**
- Tamaño máximo: 5 MB
- Formatos: JPG, JPEG, PNG, WebP, GIF

**Procesamiento automático por Cloudinary:**
- Redimensiona a 500x500px centrado en caras
- Genera thumbnail de 200x200px
- Genera avatar pequeño de 100x100px
- Optimización de calidad automática
- Conversión a WebP en navegadores compatibles
- CDN global con caché

**Response (200 OK):**
```json
{
  "message": "Imagen de perfil actualizada exitosamente",
  "profile_image": "https://res.cloudinary.com/tu_cloud/image/upload/v1234567890/steam_group/profiles/user_1.jpg",
  "url_thumbnail": "https://res.cloudinary.com/.../c_fill,h_200,w_200/user_1.jpg",
  "url_small": "https://res.cloudinary.com/.../c_fill,h_100,w_100/user_1.jpg",
  "original_size": "2340.56 KB",
  "final_size": "456.78 KB",
  "dimensions": "500x500",
  "format": "jpg"
}
```

**Uso de las URLs:**
- `profile_image`: Imagen principal (500x500) - úsala en perfiles
- `url_thumbnail`: Versión mediana (200x200) - úsala en listas
- `url_small`: Versión pequeña (100x100) - úsala en avatares

Todas las URLs son permanentes y servidas desde CDN global. Solo necesitas usar la URL directamente en tu `<img src="...">`, no requiere descarga ni procesamiento adicional.

---

### 8. Eliminar Imagen de Perfil

**Endpoint:** `DELETE /auth/profile-image`  
**Autenticación:** Requerida  
**Descripción:** Elimina la imagen de perfil del usuario

**Response (200 OK):**
```json
{
  "message": "Imagen de perfil eliminada exitosamente"
}
```

---

### 9. Obtener Todos los Usuarios

**Endpoint:** `GET /auth/users`  
**Autenticación:** Requerida  
**Descripción:** Obtiene la lista de todos los usuarios con sus datos y balance

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Usuario 1",
    "role": "master",
    "active": true,
    "profile_image": "uploads/profiles/1_abc12345.jpg",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-02T10:30:00Z",
    "auth_uid": "uuid-string-here",
    "balance": {
      "total_deposits": 500000,
      "total_expenses": 150000,
      "current_balance": 350000
    }
  },
  {
    "id": 2,
    "name": "Usuario 2",
    "role": "steam",
    "active": true,
    "profile_image": null,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "auth_uid": "uuid-string-here",
    "balance": {
      "total_deposits": 300000,
      "total_expenses": 75000,
      "current_balance": 225000
    }
  }
]
```

**Nota:** El balance se calcula dinámicamente basado en:
- `total_deposits`: Suma de todos los depósitos del usuario
- `total_expenses`: Suma de todas las partes de compras del usuario
- `current_balance`: total_deposits - total_expenses

---

## 💰 Depósitos

### 1. Crear Depósito

**Endpoint:** `POST /deposits/`  
**Autenticación:** Requerida (Solo Master)  
**Descripción:** Crea un nuevo depósito para un usuario

**Request Body:**
```json
{
  "member_id": 2,
  "amount": 100000,
  "note": "Depósito inicial",  // Opcional
  "date": "2025-01-01T00:00:00Z"  // Opcional, default: now
}
```

**Response (201 Created):**
```json
{
  "message": "Depósito registrado exitosamente",
  "deposit": {
    "id": 1,
    "member_id": 2,
    "member_name": "Juan",
    "amount": 100000,
    "note": "Depósito inicial",
    "date": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

---

### 2. Ver Depósitos de un Usuario

**Endpoint:** `GET /deposits/user/{user_id}`  
**Autenticación:** Requerida  
**Descripción:** Obtiene todos los depósitos de un usuario específico

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "member_id": 2,
    "amount": 100000,
    "note": "Depósito inicial",
    "date": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "member_id": 2,
    "amount": 50000,
    "note": "Depósito adicional",
    "date": "2025-01-15T00:00:00Z",
    "created_at": "2025-01-15T00:00:00Z"
  }
]
```

---

### 3. Ver Todos los Depósitos

**Endpoint:** `GET /deposits/`  
**Autenticación:** Requerida (Solo Master)  
**Descripción:** Obtiene todos los depósitos del sistema

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "member_id": 2,
    "amount": 100000,
    "note": "Depósito inicial",
    "date": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "member_id": 3,
    "amount": 100000,
    "note": null,
    "date": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### 4. Ver Saldo de un Usuario

**Endpoint:** `GET /deposits/balance/{user_id}`  
**Autenticación:** Requerida  
**Descripción:** Obtiene el saldo actual de un usuario (depósitos - gastos)

**Response (200 OK):**
```json
{
  "user_id": 2,
  "user_name": "Juan",
  "profile_image": "uploads/profiles/2_abc12345.jpg",
  "total_deposits": 150000,
  "total_expenses": 7200,
  "current_balance": 142800
}
```

**Nota:** Si no tiene imagen de perfil, `profile_image` será `null`

---

### 5. Ver Saldos de Todos los Usuarios

**Endpoint:** `GET /deposits/balances/all`  
**Autenticación:** Requerida (Todos los usuarios)  
**Descripción:** Obtiene los saldos de todos los usuarios activos

**Response (200 OK):**
```json
{
  "balances": [
    {
      "user_id": 2,
      "user_name": "Juan",
      "profile_image": "uploads/profiles/2_abc12345.jpg",
      "role": "steam",
      "total_deposits": 150000,
      "total_expenses": 7200,
      "current_balance": 142800
    },
    {
      "user_id": 3,
      "user_name": "Pedro",
      "profile_image": null,
      "role": "steam",
      "total_deposits": 100000,
      "total_expenses": 12000,
      "current_balance": 88000
    }
  ],
  "total_users": 5,
  "grand_total": 464000
}
```

---

## 🎮 Propuestas

### 1. Crear Propuesta

**Endpoint:** `POST /proposals/`  
**Autenticación:** Requerida  
**Descripción:** Crea una nueva propuesta de juego

**Restricciones:**
- Solo se puede tener una propuesta activa por usuario
- Estados activos: `proposed`, `voted`

**Request Body:**
```json
{
  "title": "Red Dead Redemption 2",
  "price": 100000
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Red Dead Redemption 2",
  "price": 100000,
  "proposer_id": 2,
  "status": "proposed",
  "proposal_number": 1,
  "month_year": 202501,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

### 2. Ver Todas las Propuestas

**Endpoint:** `GET /proposals/`  
**Autenticación:** No requerida  
**Descripción:** Obtiene todas las propuestas con conteo de votos

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Red Dead Redemption 2",
    "price": 100000,
    "proposer_id": 2,
    "proposer_name": "Juan",
    "status": "proposed",
    "proposal_number": 1,
    "month_year": 202501,
    "votes_count": 3,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "title": "GTA V",
    "price": 80000,
    "proposer_id": 3,
    "proposer_name": "Pedro",
    "status": "proposed",
    "proposal_number": 1,
    "month_year": 202501,
    "votes_count": 2,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### 3. Ver Propuesta Específica

**Endpoint:** `GET /proposals/{proposal_id}`  
**Autenticación:** No requerida  
**Descripción:** Obtiene los detalles de una propuesta

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Red Dead Redemption 2",
  "price": 100000,
  "proposer_id": 2,
  "proposer_name": "Juan",
  "status": "proposed",
  "proposal_number": 1,
  "month_year": 202501,
  "votes_count": 3,
  "voters": [
    {
      "voter_id": 3,
      "voter_name": "Pedro",
      "voted_at": "2025-01-02T10:00:00Z"
    },
    {
      "voter_id": 4,
      "voter_name": "María",
      "voted_at": "2025-01-02T11:00:00Z"
    }
  ],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

### 4. Votar por una Propuesta

**Endpoint:** `POST /proposals/{proposal_id}/vote`  
**Autenticación:** Requerida  
**Descripción:** Vota por una propuesta (Master SÍ puede votar)

**Restricciones:**
- No puedes votar tu propia propuesta
- Solo un voto activo por usuario
- Cambiar de voto elimina el voto anterior

**Response (200 OK) - Voto nuevo:**
```json
{
  "message": "Voto registrado exitosamente",
  "proposal_id": 1,
  "proposal_title": "Red Dead Redemption 2",
  "current_votes": 3,
  "previous_vote": null
}
```

**Response (200 OK) - Cambio de voto:**
```json
{
  "message": "Voto cambiado exitosamente",
  "proposal_id": 2,
  "proposal_title": "GTA V",
  "current_votes": 2,
  "previous_vote": {
    "proposal_id": 1,
    "proposal_title": "Red Dead Redemption 2"
  }
}
```

---

### 5. Ver Mi Voto Actual

**Endpoint:** `GET /proposals/my-vote`  
**Autenticación:** Requerida  
**Descripción:** Obtiene la propuesta por la que votó el usuario

**Response (200 OK):**
```json
{
  "has_vote": true,
  "vote": {
    "proposal_id": 1,
    "proposal_title": "Red Dead Redemption 2",
    "proposal_price": 100000,
    "voted_at": "2025-01-02T10:00:00Z"
  }
}
```

**Response (200 OK) - Sin voto:**
```json
{
  "has_vote": false,
  "vote": null
}
```

---

### 6. Seleccionar Ganador

**Endpoint:** `POST /proposals/{proposal_id}/select-winner`  
**Autenticación:** Requerida (Solo Master)  
**Descripción:** Selecciona una propuesta como ganadora

**Efecto:**
- La propuesta seleccionada cambia a estado `voted`
- Todas las demás propuestas activas cambian a `rejected`

**Response (200 OK):**
```json
{
  "message": "Propuesta seleccionada como ganadora",
  "proposal": {
    "id": 1,
    "title": "Red Dead Redemption 2",
    "price": 100000,
    "status": "voted",
    "votes_count": 3
  },
  "rejected_proposals": 2
}
```

---

### 7. Ver Mis Propuestas

**Endpoint:** `GET /proposals/my-proposals`  
**Autenticación:** Requerida  
**Descripción:** Obtiene todas las propuestas del usuario autenticado

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Red Dead Redemption 2",
    "price": 100000,
    "status": "voted",
    "votes_count": 3,
    "created_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": 5,
    "title": "FIFA 24",
    "price": 50000,
    "status": "rejected",
    "votes_count": 0,
    "created_at": "2024-12-01T00:00:00Z"
  }
]
```

---

## 🛒 Compras

### 1. Crear Compra desde Propuesta

**Endpoint:** `POST /purchases/from-proposal/{proposal_id}`  
**Autenticación:** Requerida (Solo Master)  
**Descripción:** Crea una compra desde una propuesta aprobada y descuenta saldos

**División de costos:**
- Propietario (proposer): 40%
- Otros 5 usuarios: 60% ÷ 5 = 12% cada uno

**Request Body:**
```json
{
  "was_on_sale": false,  // Opcional, default: false
  "original_price": 150000  // Opcional, solo si was_on_sale = true
}
```

**Response (201 Created):**
```json
{
  "message": "Compra registrada y saldos descontados exitosamente",
  "purchase": {
    "id": 1,
    "title": "Red Dead Redemption 2",
    "total_price": 100000,
    "owner_id": 2,
    "owner_name": "Juan",
    "proposal_id": 1,
    "was_on_sale": false,
    "original_price": null,
    "purchased_at": "2025-01-03T00:00:00Z"
  },
  "shares": [
    {
      "member_id": 2,
      "member_name": "Juan",
      "share_amount": 40000,
      "percentage": 40,
      "paid": true,
      "is_owner": true
    },
    {
      "member_id": 3,
      "member_name": "Pedro",
      "share_amount": 12000,
      "percentage": 12,
      "paid": true,
      "is_owner": false
    }
    // ... otros 4 usuarios
  ],
  "proposal_status": "purchased"
}
```

**Validaciones:**
- La propuesta debe estar en estado `voted`
- Todos los usuarios deben tener saldo suficiente
- Se crean 6 shares (1 owner + 5 participants)

---

### 2. Crear Compra Manual

**Endpoint:** `POST /purchases/?owner_id={owner_id}`  
**Autenticación:** Requerida (Solo Master)  
**Descripción:** Crea una compra manual sin propuesta asociada

**Query Parameters:**
- `owner_id` (required): ID del usuario propietario

**Request Body:**
```json
{
  "title": "God of War",
  "total_price": 40000,
  "was_on_sale": true,
  "original_price": 60000
}
```

**Response (201 Created):**
```json
{
  "message": "Compra registrada y saldos descontados exitosamente",
  "purchase": {
    "id": 2,
    "title": "God of War",
    "total_price": 40000,
    "owner_id": 2,
    "owner_name": "Juan",
    "proposal_id": null,
    "was_on_sale": true,
    "original_price": 60000,
    "purchased_at": "2025-01-05T00:00:00Z"
  },
  "shares": [
    // Mismo formato que compra desde propuesta
  ]
}
```

---

### 3. Ver Todas las Compras

**Endpoint:** `GET /purchases/`  
**Autenticación:** Requerida  
**Descripción:** Obtiene todas las compras del sistema

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Red Dead Redemption 2",
    "total_price": 100000,
    "owner_id": 2,
    "owner_name": "Juan",
    "proposal_id": 1,
    "was_on_sale": false,
    "original_price": null,
    "purchased_at": "2025-01-03T00:00:00Z",
    "participants_count": 6
  },
  {
    "id": 2,
    "title": "God of War",
    "total_price": 40000,
    "owner_id": 2,
    "owner_name": "Juan",
    "proposal_id": null,
    "was_on_sale": true,
    "original_price": 60000,
    "purchased_at": "2025-01-05T00:00:00Z",
    "participants_count": 6
  }
]
```

---

### 4. Ver Compra Específica

**Endpoint:** `GET /purchases/{purchase_id}`  
**Autenticación:** Requerida  
**Descripción:** Obtiene los detalles completos de una compra

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Red Dead Redemption 2",
  "total_price": 100000,
  "owner_id": 2,
  "owner_name": "Juan",
  "proposal_id": 1,
  "was_on_sale": false,
  "original_price": null,
  "purchased_at": "2025-01-03T00:00:00Z",
  "shares": [
    {
      "id": 1,
      "member_id": 2,
      "member_name": "Juan",
      "share_amount": 40000,
      "paid": true,
      "created_at": "2025-01-03T00:00:00Z"
    },
    {
      "id": 2,
      "member_id": 3,
      "member_name": "Pedro",
      "share_amount": 12000,
      "paid": true,
      "created_at": "2025-01-03T00:00:00Z"
    }
    // ... otros participantes
  ]
}
```

---

### 5. Ver Mis Compras (Como Propietario)

**Endpoint:** `GET /purchases/my-purchases`  
**Autenticación:** Requerida  
**Descripción:** Obtiene las compras donde el usuario es el propietario

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Red Dead Redemption 2",
    "total_price": 100000,
    "my_share": 40000,
    "was_on_sale": false,
    "original_price": null,
    "purchased_at": "2025-01-03T00:00:00Z",
    "participants_count": 6
  },
  {
    "id": 2,
    "title": "God of War",
    "total_price": 40000,
    "my_share": 16000,
    "was_on_sale": true,
    "original_price": 60000,
    "purchased_at": "2025-01-05T00:00:00Z",
    "participants_count": 6
  }
]
```

---

### 6. Ver Mis Participaciones

**Endpoint:** `GET /purchases/my-participations`  
**Autenticación:** Requerida  
**Descripción:** Obtiene las compras donde el usuario es participante (no propietario)

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "title": "Cyberpunk 2077",
    "total_price": 60000,
    "owner_id": 4,
    "owner_name": "María",
    "my_share": 7200,
    "was_on_sale": false,
    "original_price": null,
    "purchased_at": "2025-01-10T00:00:00Z"
  },
  {
    "id": 4,
    "title": "Elden Ring",
    "total_price": 50000,
    "owner_id": 3,
    "owner_name": "Pedro",
    "my_share": 6000,
    "was_on_sale": true,
    "original_price": 80000,
    "purchased_at": "2025-01-12T00:00:00Z"
  }
]
```

---

## 📊 Códigos de Estado HTTP

### Códigos de Éxito

| Código | Descripción |
|--------|-------------|
| `200 OK` | Solicitud exitosa |
| `201 Created` | Recurso creado exitosamente |

### Códigos de Error del Cliente

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `400 Bad Request` | Solicitud inválida | Datos faltantes, formato incorrecto |
| `401 Unauthorized` | No autenticado | Token inválido o expirado |
| `403 Forbidden` | Sin permisos | Usuario normal intentando acción de master |
| `404 Not Found` | Recurso no encontrado | Usuario, propuesta o compra no existe |

### Códigos de Error del Servidor

| Código | Descripción |
|--------|-------------|
| `500 Internal Server Error` | Error interno del servidor |
| `503 Service Unavailable` | Servicio no disponible (BD desconectada) |

---

## 📦 Modelos de Datos

### SteamUser (Usuario)

```typescript
{
  id: number,
  name: string,
  role: "steam" | "master",
  active: boolean,
  profile_image: string | null,
  created_at: string (ISO 8601),
  updated_at: string (ISO 8601),
  auth_uid: string (UUID)
}
```

---

### Deposit (Depósito)

```typescript
{
  id: number,
  member_id: number,
  amount: number,
  note: string | null,
  date: string (ISO 8601),
  created_at: string (ISO 8601)
}
```

---

### GameProposal (Propuesta de Juego)

```typescript
{
  id: number,
  title: string,
  price: number,
  proposer_id: number,
  status: "proposed" | "voted" | "rejected" | "purchased",
  proposal_number: number,
  month_year: number,  // Formato: YYYYMM (ej: 202501)
  created_at: string (ISO 8601),
  updated_at: string (ISO 8601)
}
```

**Estados:**
- `proposed`: Propuesta creada, esperando votación
- `voted`: Propuesta aprobada por el master
- `rejected`: Propuesta rechazada
- `purchased`: Juego ya comprado

---

### Vote (Voto)

```typescript
{
  id: number,
  proposal_id: number,
  member_id: number,
  created_at: string (ISO 8601)
}
```

---

### Purchase (Compra)

```typescript
{
  id: number,
  title: string,
  total_price: number,
  owner_id: number,
  proposal_id: number | null,
  was_on_sale: boolean,
  original_price: number | null,
  purchased_at: string (ISO 8601)
}
```

---

### PurchaseShare (Participación en Compra)

```typescript
{
  id: number,
  purchase_id: number,
  member_id: number,
  share_amount: number,
  paid: boolean,
  created_at: string (ISO 8601)
}
```

---

## 🔒 Autenticación y Autorización

### Tipos de Autenticación

**1. Cookies HTTPOnly:**
- Todas las peticiones autenticadas requieren cookies
- `steam_access_token`: Token de acceso (corta duración)
- `steam_refresh_token`: Token de refresco (larga duración)

**2. Roles de Usuario:**
- `steam`: Usuario normal
- `master`: Usuario administrador

### Permisos por Rol

| Acción | Steam | Master |
|--------|-------|--------|
| Ver propuestas | ✅ | ✅ |
| Crear propuestas | ✅ | ✅ |
| Votar propuestas | ✅ | ✅ |
| Seleccionar ganador | ❌ | ✅ |
| Ver saldos (todos) | ✅ | ✅ |
| Ver saldo (propio) | ✅ | ✅ |
| Crear depósitos | ❌ | ✅ |
| Ver todos los depósitos | ❌ | ✅ |
| Crear compras | ❌ | ✅ |
| Ver compras | ✅ | ✅ |
| Subir/eliminar foto perfil | ✅ | ✅ |

---

## 🌐 CORS y Configuración

**Orígenes permitidos:**
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

**Headers permitidos:**
- Todos (`*`)

**Métodos permitidos:**
- Todos (`*`)

**Credenciales:**
- Habilitadas (`allow_credentials: true`)

---

## 📝 Notas Importantes

### Cálculo de Saldos

El saldo de un usuario se calcula dinámicamente:

```
current_balance = total_deposits - total_expenses
```

Donde:
- `total_deposits`: Suma de todos los depósitos del usuario
- `total_expenses`: Suma de todos los `share_amount` donde `paid = true`

### División de Costos en Compras

**Fórmula:**
- Propietario: `40%` del precio total
- Cada participante: `12%` del precio total (60% ÷ 5)

**Ejemplo con juego de $100,000:**
- Propietario: $40,000
- Participante 1: $12,000
- Participante 2: $12,000
- Participante 3: $12,000
- Participante 4: $12,000
- Participante 5: $12,000
- **Total:** $100,000 ✅

### Archivos Estáticos (Imágenes)

**URL de imágenes:**
```
http://localhost:8000/uploads/profiles/{filename}
```

**Ejemplo:**
```
http://localhost:8000/uploads/profiles/2_abc12345.jpg
```

**Uso en frontend:**
```javascript
const avatarUrl = user.profile_image 
  ? `http://localhost:8000/${user.profile_image}`
  : '/default-avatar.png';
```

---

## 🚀 Swagger UI

**URL:** `http://localhost:8000/docs`

Swagger UI proporciona:
- ✅ Interfaz interactiva para probar todos los endpoints
- ✅ Documentación automática de schemas
- ✅ Pruebas de autenticación con cookies
- ✅ Upload de archivos (imágenes)

---

## 📞 Endpoints de Sistema

### Health Check

**Endpoint:** `GET /`  
**Autenticación:** No requerida

**Response (200 OK):**
```json
{
  "message": "Bienvenido a la API de Steam Group Management",
  "status": "online",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

### Database Health

**Endpoint:** `GET /health`  
**Autenticación:** No requerida

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "Database connection failed: error message"
}
```

---

## 🎯 Flujo Completo de Usuario

### 1. Registro y Autenticación
```
POST /auth/register → Login automático
POST /auth/login → Obtener cookies
GET /auth/me → Verificar sesión
POST /auth/upload-profile-image → Subir avatar
```

### 2. Ver Saldos
```
GET /deposits/balances/all → Ver todos los saldos
GET /deposits/balance/{user_id} → Ver saldo individual
```

### 3. Crear y Votar Propuestas
```
POST /proposals/ → Crear propuesta
GET /proposals/ → Ver todas las propuestas
POST /proposals/{id}/vote → Votar
GET /proposals/my-vote → Ver mi voto
```

### 4. Compra (Master)
```
POST /proposals/{id}/select-winner → Aprobar propuesta
POST /purchases/from-proposal/{id} → Comprar juego
GET /purchases/my-purchases → Ver mis compras
```

### 5. Depósitos (Master)
```
POST /deposits/ → Crear depósito
GET /deposits/balances/all → Verificar saldos actualizados
```

---

**📌 Última actualización:** Noviembre 15, 2025  
**🔗 Base URL:** `http://localhost:8000`  
**📖 Swagger Docs:** `http://localhost:8000/docs`
