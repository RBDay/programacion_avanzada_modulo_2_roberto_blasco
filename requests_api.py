import requests

base_url = "http://127.0.0.1:8001/"
base_api_notes = "api/notes/"


#comprobamos que el backend está corriendo
request = requests.get(base_url);
print(request.status_code, request.reason, request.text);

#creamos notas de prueba
request = requests.post(base_url + base_api_notes, json={
    "title": "Nota de prueba 1",
    "content": "Contenido de la nota de prueba 1",
    "deadline": "2027-12-31T23:59:59",
    "completed": False,
    "published": True
})
print(request.status_code, request.reason, request.text);

request = requests.post(base_url + base_api_notes, json={
    "title": "Nota de prueba 2",
    "content": "Contenido de la nota de prueba 2",
    "deadline": "2027-12-31T23:59:59",
    "completed": False,
    "published": True
})
print(request.status_code, request.reason, request.text);

request = requests.post(base_url + base_api_notes, json={
    "title": "Nota de prueba 3",
    "content": "Contenido de la nota de prueba 3",
    "deadline": "2024-12-31T23:59:59",
    "completed": False,
    "published": True
})
print(request.status_code, request.reason, request.text);

#comprobamos que podemos ver todas las notas (excluyendo las caducadas) y las notas caducadas
request_list_notes = requests.get(base_url + base_api_notes)
print(request_list_notes.status_code, request_list_notes.reason, request_list_notes.text);

request_list_notes_expired = requests.get(base_url + base_api_notes + "expired/list")
print(request_list_notes_expired.status_code, request_list_notes_expired.reason, request_list_notes_expired.text);

#cojemos el id e una de las caducadas y otra de las no caducadas
note_id_expired = request_list_notes_expired.json()[0]["id"]
note_id_not_expired = request_list_notes.json()[0]["id"]

#comprobamos la actualización
request_update_note = requests.put(base_url + base_api_notes + str(note_id_not_expired), json={
    "title": "Nota de prueba 1 actualizada",
    "content": "Contenido de la nota de prueba 1 actualizado",
    "deadline": "2027-12-31T23:59:59",
    "completed": True,
    "published": True
})
print(request_update_note.status_code, request_update_note.reason, request_update_note.text); #<------ este debería dar un 200 OK

request_update_note_expired = requests.put(base_url + base_api_notes + str(note_id_expired), json={
    "title": "Nota de prueba 3 actualizada",
    "content": "Contenido de la nota de prueba 3 actualizado",
    "deadline": "2024-12-31T23:59:59",
    "completed": True,
    "published": True
})
print(request_update_note_expired.status_code, request_update_note_expired.reason, request_update_note_expired.text); #<------ este debería dar un 400 Bad Request porque la nota está caducada

#comprobamos la ruta de mark_completed
request_mark_completed = requests.patch(base_url + base_api_notes + str(note_id_not_expired) + "/mark_completed")
print(request_mark_completed.status_code, request_mark_completed.reason, request_mark_completed.text); 

request_mark_completed_expired = requests.patch(base_url + base_api_notes + str(note_id_expired) + "/mark_completed")
print(request_mark_completed_expired.status_code, request_mark_completed_expired.reason, request_mark_completed_expired.text);

#comprobamos la ruta de borrado
request_delete_note = requests.delete(base_url + base_api_notes + str(note_id_not_expired))
print(request_delete_note.status_code, request_delete_note.reason, request_delete_note.text);

request_delete_note_expired = requests.delete(base_url + base_api_notes + str(note_id_expired))
print(request_delete_note_expired.status_code, request_delete_note_expired.reason, request_delete_note_expired.text); #<------ este debería dar un 400 Bad Request porque la nota está caducada