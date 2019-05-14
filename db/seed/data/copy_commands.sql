\copy "Senadors"(id,nombre,apellido_paterno,apellido_materno,partido_politico,telefono,email,url_curriculum,url_foto,url_twitter) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/senadors.csv' DELIMITER ',' CSV HEADER;

\copy "Proyectos"(id,boletin,fecha,resumen,estado,url) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/proyectos.csv' DELIMITER ',' CSV HEADER;

\copy "Periodos"(sid,cargo,inicio,final) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/periodos.csv' DELIMITER ',' CSV HEADER;

\copy "SenadorProyectos"(sid,pid) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/senador_proyectos.csv' DELIMITER ',' CSV HEADER;
