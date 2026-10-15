import os
import socket
import sys
import time
import requests

# Determinar URL de la API:
# 1. Variable de entorno API_URL (si está definida)
# 2. Argumento de línea de comandos (si se especifica)
# 3. 'http://api:8000' si resuelve el host 'api' (entorno Docker Compose)
# 4. 'http://127.0.0.1:8001' si estamos ejecutando directamente desde el host
def get_base_url():
    if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        return sys.argv[1].rstrip("/") + "/"
    if os.getenv("API_URL"):
        return os.getenv("API_URL").rstrip("/") + "/"
    try:
        socket.gethostbyname("api")
        return "http://api:8000/"
    except socket.gaierror:
        return "http://127.0.0.1:8001/"

base_url = get_base_url()
base_api_notes = "api/notes/"

total_tests = 0
passed_tests = 0
failed_tests = 0

def test_step(step_name, expected_status, request_func, validate_fn=None):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    try:
        res = request_func()
        status_ok = res.status_code == expected_status
        custom_ok = True
        custom_err = ""
        if status_ok and validate_fn:
            try:
                custom_ok = validate_fn(res)
            except Exception as e:
                custom_ok = False
                custom_err = f" (Validación falló: {e})"

        if status_ok and custom_ok:
            passed_tests += 1
            print(f"  [OK] {step_name} -> {res.status_code} {res.reason}")
            return res
        else:
            failed_tests += 1
            err_info = custom_err if not custom_ok else f" (Esperado: {expected_status}, Obtenido: {res.status_code})"
            print(f"  [FAIL] {step_name} -> {res.status_code} {res.reason}{err_info}")
            print(f"         Respuesta: {res.text[:180]}")
            return res
    except Exception as e:
        failed_tests += 1
        print(f"  [ERROR] {step_name} -> Excepción: {e}")
        return None


print("=" * 70)
print(" SUITE DE PRUEBAS AUTOMATIZADAS - API DE NOTAS")
print(f" Destino API: {base_url}")
print("=" * 70)

# 0. Espera activa a que el backend esté disponible
print("\n[0/8] Esperando a que el backend esté disponible...")
max_retries = 30
connected = False
for i in range(1, max_retries + 1):
    try:
        r = requests.get(base_url, timeout=3)
        if r.status_code == 200:
            print(f"  -> Conexión establecida con éxito en el intento {i}.")
            connected = True
            break
    except Exception:
        pass
    time.sleep(1)

if not connected:
    print(f"  [FATAL] No se pudo conectar al API en {base_url} tras {max_retries} segundos.")
    sys.exit(1)

# 1. Comprobamos que el backend está corriendo
print("\n[1/8] Verificación del Endpoint Raíz (GET /):")
test_step(
    "Comprobar endpoint raíz GET /",
    200,
    lambda: requests.get(base_url),
    lambda r: "msg" in r.json()
)

# 2. Creación de notas de prueba y validaciones de POST
print("\n[2/8] Endpoint POST /api/notes/ (Creación y Validaciones):")
# Creamos nota de prueba activa 1
resp_nota1 = test_step(
    "Crear nota de prueba 1 (activa)",
    201,
    lambda: requests.post(base_url + base_api_notes, json={
        "title": "Nota de prueba 1",
        "content": "Contenido de la nota de prueba 1",
        "deadline": "2027-12-31T23:59:59",
        "completed": False,
        "published": True
    })
)

# Creamos nota de prueba activa 2
resp_nota2 = test_step(
    "Crear nota de prueba 2 (activa)",
    201,
    lambda: requests.post(base_url + base_api_notes, json={
        "title": "Nota de prueba 2",
        "content": "Contenido de la nota de prueba 2",
        "deadline": "2027-12-31T23:59:59",
        "completed": False,
        "published": True
    })
)

# Creamos nota de prueba caducada 3
resp_nota3 = test_step(
    "Crear nota de prueba 3 (caducada en 2024)",
    201,
    lambda: requests.post(base_url + base_api_notes, json={
        "title": "Nota de prueba 3",
        "content": "Contenido de la nota de prueba 3",
        "deadline": "2024-12-31T23:59:59",
        "completed": False,
        "published": True
    })
)

# Validaciones de error en POST
test_step(
    "Validación POST: Faltan campos obligatorios (body vacío)",
    422,
    lambda: requests.post(base_url + base_api_notes, json={})
)

test_step(
    "Validación POST: Título excede los 100 caracteres",
    422,
    lambda: requests.post(base_url + base_api_notes, json={
        "title": "A" * 101,
        "content": "Contenido",
        "deadline": "2027-12-31T23:59:59"
    })
)

test_step(
    "Validación POST: Formato de fecha deadline inválido",
    422,
    lambda: requests.post(base_url + base_api_notes, json={
        "title": "Nota fecha inválida",
        "content": "Contenido",
        "deadline": "fecha-invalida"
    })
)

# 3. Comprobamos listados de notas (GET /api/notes/ y GET /api/notes/expired/list)
print("\n[3/8] Endpoints GET /api/notes/ (Listados y Filtros):")
req_list_notes = test_step(
    "Listar notas activas (excluye caducadas por defecto)",
    200,
    lambda: requests.get(base_url + base_api_notes),
    lambda r: isinstance(r.json(), list) and len(r.json()) > 0
)

req_list_notes_all = test_step(
    "Listar todas las notas con include_expired=True",
    200,
    lambda: requests.get(base_url + base_api_notes, params={"include_expired": True}),
    lambda r: isinstance(r.json(), list)
)

req_list_notes_expired = test_step(
    "Listar notas caducadas GET /api/notes/expired/list",
    200,
    lambda: requests.get(base_url + base_api_notes + "expired/list"),
    lambda r: isinstance(r.json(), list) and len(r.json()) > 0
)

# Recuperar IDs para las siguientes pruebas
try:
    note_id_not_expired = resp_nota1.json()["id"] if resp_nota1 and resp_nota1.status_code == 201 else req_list_notes.json()[0]["id"]
    note_id_expired = resp_nota3.json()["id"] if resp_nota3 and resp_nota3.status_code == 201 else req_list_notes_expired.json()[0]["id"]
except Exception as e:
    print(f"  [ERROR] No se pudieron obtener los IDs de notas para pruebas posteriores: {e}")
    sys.exit(1)

print(f"  -> Usando ID de nota activa: {note_id_not_expired}")
print(f"  -> Usando ID de nota caducada: {note_id_expired}")

# 4. Obtener nota por ID (GET /api/notes/{id})
print("\n[4/8] Endpoint GET /api/notes/{id} (Consulta por ID y Validaciones):")
test_step(
    f"Obtener nota activa por ID ({note_id_not_expired})",
    200,
    lambda: requests.get(base_url + base_api_notes + str(note_id_not_expired)),
    lambda r: r.json()["id"] == note_id_not_expired
)

test_step(
    f"Validación GET: Obtener nota caducada ({note_id_expired}) debe retornar 400 Bad Request",
    400,
    lambda: requests.get(base_url + base_api_notes + str(note_id_expired))
)

test_step(
    "Validación GET: Obtener nota inexistente (ID 999999) debe retornar 404",
    404,
    lambda: requests.get(base_url + base_api_notes + "999999")
)

test_step(
    "Validación GET: ID no numérico debe retornar 422",
    422,
    lambda: requests.get(base_url + base_api_notes + "cadena-invalida")
)

# 5. Comprobamos la actualización (PUT /api/notes/{id})
print("\n[5/8] Endpoint PUT /api/notes/{id} (Actualización y Validaciones):")
test_step(
    f"Actualizar nota activa ({note_id_not_expired}) -> 200 OK",
    200,
    lambda: requests.put(base_url + base_api_notes + str(note_id_not_expired), json={
        "title": "Nota de prueba 1 actualizada",
        "content": "Contenido de la nota de prueba 1 actualizado",
        "deadline": "2027-12-31T23:59:59",
        "completed": True,
        "published": True
    }),
    lambda r: r.json()["title"] == "Nota de prueba 1 actualizada"
)

test_step(
    f"Validación PUT: Actualizar nota caducada ({note_id_expired}) debe retornar 400 Bad Request",
    400,
    lambda: requests.put(base_url + base_api_notes + str(note_id_expired), json={
        "title": "Nota de prueba 3 actualizada",
        "content": "Contenido de la nota de prueba 3 actualizado",
        "deadline": "2024-12-31T23:59:59",
        "completed": True,
        "published": True
    })
)

test_step(
    "Validación PUT: Actualizar nota inexistente (ID 999999) debe retornar 404",
    404,
    lambda: requests.put(base_url + base_api_notes + "999999", json={
        "title": "Inexistente"
    })
)

test_step(
    f"Validación PUT: Título excede los 100 caracteres debe retornar 422",
    422,
    lambda: requests.put(base_url + base_api_notes + str(note_id_not_expired), json={
        "title": "A" * 101
    })
)

# 6. Comprobamos la ruta de mark_completed (PATCH /api/notes/{id}/mark_completed)
print("\n[6/8] Endpoint PATCH /api/notes/{id}/mark_completed (Completar nota):")
test_step(
    f"Marcar nota activa ({note_id_not_expired}) como completada -> 200 OK",
    200,
    lambda: requests.patch(base_url + base_api_notes + str(note_id_not_expired) + "/mark_completed"),
    lambda r: r.json()["completed"] is True
)

test_step(
    f"Validación PATCH: Marcar nota caducada ({note_id_expired}) debe retornar 400 Bad Request",
    400,
    lambda: requests.patch(base_url + base_api_notes + str(note_id_expired) + "/mark_completed")
)

test_step(
    "Validación PATCH: Marcar nota inexistente (ID 999999) debe retornar 404",
    404,
    lambda: requests.patch(base_url + base_api_notes + "999999/mark_completed")
)

# 7. Comprobamos la ruta de borrado (DELETE /api/notes/{id})
print("\n[7/8] Endpoint DELETE /api/notes/{id} (Eliminación y Validaciones):")
test_step(
    f"Validación DELETE: Eliminar nota caducada ({note_id_expired}) debe retornar 400 Bad Request",
    400,
    lambda: requests.delete(base_url + base_api_notes + str(note_id_expired))
)

test_step(
    f"Eliminar nota activa ({note_id_not_expired}) -> 200 OK",
    200,
    lambda: requests.delete(base_url + base_api_notes + str(note_id_not_expired))
)

test_step(
    f"Validación DELETE: Eliminar nota ya eliminada ({note_id_not_expired}) debe retornar 404",
    404,
    lambda: requests.delete(base_url + base_api_notes + str(note_id_not_expired))
)

test_step(
    "Validación DELETE: Eliminar nota inexistente (ID 999999) debe retornar 404",
    404,
    lambda: requests.delete(base_url + base_api_notes + "999999")
)

# 8. Resumen final
print("\n" + "=" * 70)
print(f" RESUMEN DE PRUEBAS: {passed_tests}/{total_tests} pruebas superadas.")
if failed_tests > 0:
    print(f" [FALLO] Hubo {failed_tests} prueba(s) que fallaron.")
    print("=" * 70)
    sys.exit(1)
else:
    print(" [ÉXITO] Todos los endpoints y sus validaciones funcionan correctamente.")
    print("=" * 70)
    sys.exit(0)