# 🚀 Despliegue en Render - Guía Rápida

## 📋 Archivos Preparados

✅ `build.sh` - Script de instalación
✅ `render.yaml` - Configuración de Render
✅ `main.py` - Actualizado con soporte para Render
✅ `app/database.py` - Compatible con PostgreSQL de Render

---

## 🔧 Pasos para Desplegar

### 1. Subir a GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin master
```

### 2. Crear cuenta en Render

1. Ve a https://render.com
2. Click en "Get Started"
3. Regístrate con GitHub

### 3. Crear Web Service

1. En el dashboard, click "New +" → "Web Service"
2. Conecta tu repositorio GitHub `Ecomerce`
3. Render detectará automáticamente el `render.yaml`

### 4. Configuración Automática

Render leerá el archivo `render.yaml` y creará:
- ✅ Web Service (API)
- ✅ PostgreSQL Database (gratis)
- ✅ Variables de entorno

### 5. Configurar Variables de Entorno

En el dashboard del Web Service, agrega manualmente:

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_key_de_supabase
```

*Nota: JWT_SECRET_KEY y DATABASE_URL se generan automáticamente*

### 6. Deploy

1. Click "Create Web Service"
2. Espera 3-5 minutos
3. Tu API estará en: `https://steam-api.onrender.com`

---

## 🗄️ Opción: Usar Supabase en lugar de Render PostgreSQL

Si prefieres mantener Supabase como base de datos:

1. En `render.yaml`, elimina la sección `databases`
2. En variables de entorno, agrega:
   ```
   DATABASE_URL=tu_connection_string_de_supabase
   ```

---

## 📝 Variables de Entorno Necesarias

```env
# Automáticas (Render las genera)
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
JWT_REFRESH_SECRET_KEY=...
PYTHON_VERSION=3.11.0

# Debes configurar manualmente
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
```

---

## ✅ Verificar Deployment

Una vez desplegado, prueba:

```bash
# Health check
curl https://steam-api.onrender.com/health

# Docs
https://steam-api.onrender.com/docs
```

---

## ⚠️ Nota Importante: Cold Start

El plan gratuito de Render "duerme" después de 15 minutos de inactividad.
La primera petición después de despertar puede tardar ~30 segundos.

**Solución:** Usar UptimeRobot (gratis) para hacer ping cada 5 minutos.

---

## 🐛 Troubleshooting

### Error: "Build failed"
- Verifica que `build.sh` tiene permisos de ejecución
- En Render, el archivo debe tener `chmod +x build.sh`

### Error: "Database connection failed"
- Verifica que DATABASE_URL está configurada
- Asegúrate que la BD de Render está creada

### Error: "Module not found"
- Verifica que todas las dependencias están en `requirements.txt`
- Ejecuta localmente: `pip freeze > requirements.txt`

---

## 📞 URLs Importantes

- Dashboard Render: https://dashboard.render.com
- Docs de Render: https://render.com/docs
- Support: https://render.com/support

---

**¡Listo para Deploy!** 🚀

Siguiente paso: `git push origin master` y luego ir a Render.
