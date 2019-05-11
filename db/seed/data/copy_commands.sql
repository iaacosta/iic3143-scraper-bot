\copy "Senadors"(id,nombre,apellido_paterno,apellido_materno,partido_politico,telefono,email,url_curriculum,url_foto,url_twitter) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/senators.csv' DELIMITER ',' CSV HEADER;

\copy "Proyectos"(id,boletin,fecha,resumen,estado,url) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/proyectos.csv' DELIMITER ',' CSV HEADER;

\copy "Periodos"(sid,cargo,inicio,final) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/periods.csv' DELIMITER ',' CSV HEADER;

\copy "SenadorProyectos"(sid,pid) FROM PROGRAM 'curl http://167.99.10.105:3000/csv/leyes_por_senador.csv' DELIMITER ',' CSV HEADER;
