import sys
import csv
import time
import requests # Version: 2.31.0
import openai   # Version: 0.28.0
import os
os.system("")

google_key = "AIzaSyBpQAWr363iBXFozFp4V9uE-U2Yb5EwvUQ"
openai_key = "sk-proj-xrC4dqSD1pRNgOdWCHPUT3BlbkFJYoxw7TdsS1yBWKMHEFRO"
#get_data_results = []

def get_info(search, city, country):
    query = f"{search} en {city} {country}"
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": google_key}
    response = requests.get(base_url, params=params)
    limit = 10
    counter = 0
    results = []
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            print(f" ---> RESULTADOS DE LA BUSQUEDA DE: {search} en {city}, {country}")
            for site in data["results"]:
                if counter < limit:
                    place_id  = site['place_id']
                    name = site['name']
                    address = site.get("formatted_address", "No disponible")
                    rating = site.get("rating", "No disponible")
                    photo_url = 'No disponible'
                    phone = 'No disponible'
                    types_list = site.get("types", [])
                    types = ", ".join(types_list)
                    website = 'No disponible'
                    iframe = 'No disponible'
                    if "photos" in site:
                        photo_reference = site["photos"][0]["photo_reference"]
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={google_key}"
#---INICIO-SECTOR-DETALLES--------------------------------------------------------------------------#
                    url_details = "https://maps.googleapis.com/maps/api/place/details/json"
                    params_details = {"place_id": place_id, "key": google_key}
                    response_details = requests.get(url_details, params=params_details)
                    if response_details.status_code == 200:
                        details = response_details.json()
                        if details and "result" in details:
                            if "international_phone_number" in details["result"]:
                                phone = details["result"]["international_phone_number"].replace(" ","")
                            if "website" in details["result"]:
                                website = details["result"]["website"]
                            if "geometry" in details["result"]:
                                location = details["result"]["geometry"]["location"]
                                sanitized_name = name.replace(" ", "+").replace(".", "+").replace("|","").upper()
                                coordinate = f"{location['lat']},{location['lng']}"
                                iframe = f"https://www.google.com/maps/embed/v1/place?q={sanitized_name}&center={coordinate}&key={google_key}"
                    else:
                        print(f" ---> ERROR AL BUSCAR DETALLES PARA: {name}")
#---FIN-SECTOR-DETALLES----------------------------------------------------------------------------#
#---INICIO-SECTOR-OPENAI--->-DESCIPCION-DEL-LUGAR--------------------------------------------------#
                    
                    openai.api_key = openai_key
                    order = f"Actua como un experto en marketing, realiza una breve descripcion de un maximo de 50 palabras de lugar para incluirla en mi sitio web, evita exagerar" 
                    content = f"Tematica {search}: El lugar es {name} en {address}, {city}, {country}. Los types del lugar son: {types}"
                    context = {"role": "system", "content": order}
                    messages = [context]
                    messages.append({"role": "user", "content": content})
                    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                    response_content = response.choices[0].message.content
                    messages.append({"role": "assistant", "content": response_content})
                    description = response_content
                    
#---FIN-SECTOR-OPENAI--->-DESCIPCION-DEL-LUGAR-----------------------------------------------------# 
                    
                    site_data = {
                        "Pais": country,
                        "Ciudad": city,
                        "Nombre": name,
                        "Direccion": address,
                        "Valoración": rating,
                        "Foto": photo_url,
                        "Telefono": phone,
                        "Servicios": types,
                        "Sitio Web": website,
                        "Enlace para Iframe": iframe,
                        "Descripcion": description
                    }
                    print(f"---------- RESULTADO NUMERO {counter+1} ----------")
                    for key, value in site_data.items():
                        print(f"-> {key}: {value}")
                    print(f"----------------------------------------")
                    results.append(site_data)
                    counter += 1
        else:
            print(f" ---> NO SE ENCONTRARON RESULTADOS PARA {search} EN {city}, {country}.")
            
#---INICIO-SECTOR-EXPORTACION-DE-DATOS----------------------------------------------#
        
        with open(f"Data_{city}.csv", "w", newline="") as csvfile:
            fieldnames = ["Pais", "Ciudad", "Nombre", "Direccion", "Valoración", "Foto", "Telefono", "Servicios", "Sitio Web", "Enlace para Iframe", "Descripcion"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        print(f" ---> DATOS EXPORTADOS CORRECTAMENTE --> 'Data_{city}.csv' ")

#---FIN-SECTOR-EXPORTACION-DE-DATOS---------------------------------------------------------#

#---INICIO-SECTOR-OPENAI--->-DESCIPCION-DEL-LA-CIUDAD----------------------------------------------#

        openai.api_key = openai_key
        print(f" ---> GENERANDO DESCRIPCION DE LA CIUDAD VIA OPENAI")
        order = f"Actua como un experto en marketing, realiza una breve descripcion de un maximo de 50 palabras ciudad teniendo en cuenta la tematica, evita exagerar" 
        content = f"Tematica {search}: La ciudad es {city} en {country}."
        context = {"role": "system", "content": order}
        messages = [context]
        messages.append({"role": "user", "content": content})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        response_content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": response_content})
        description_city = response_content
        print(f" ---> DESCRIPCION DE LA CUIDAD GENERADA CORRECTAMENTE")

#---FIN-SECTOR-OPENAI--->-DESCIPCION-DEL-LA-CIUDAD-------------------------------------------------# 

#---INICIO-SECTOR-OPENAI--->-TEXTO-INTRODUCTORIO-DEL-LA-LISTA--------------------------------------#

        openai.api_key = openai_key
        print(f" ---> GENERANDO TEXTO INTRODUCTORIO LA LISTA VIA OPENAI")
        order = f"Actua como un experto en marketing, realiza un texto introductorio a una lista de {limit} lugares, debe comenzar con 'A continuacion presentamos una lista con {limit}...' con un maximo de 50 palabras teniendo muy en cuenta la tematica, evita exagerar" 
        content = f"Tematica {search}: La ciudad es {city} en {country}."
        context = {"role": "system", "content": order}
        messages = [context]
        messages.append({"role": "user", "content": content})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        response_content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": response_content})
        introductory_text = response_content
        print(f" ---> TEXTO INTRODUCTORIO A LA LISTA GENERADO CORRECTAMENTE")

#---FIN-SECTOR-OPENAI--->-TEXTO-INTRODUCTORIO-DEL-LA-LISTA--------------------------------------# 

#---INICIO-SECTOR-PLANTILLA---------------------------------------------------------------------#

        html_content = f'''
        
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Las Mejores {search} en {city}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<!-- wp:html -->
<h1 class="heading">Las Mejores <span class="underline--magical">{search} en {city} </span> </h1>
<!-- /wp:html -->

<!-- wp:paragraph -->
<p>{description_city} </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{introductory_text}</p>
<!-- /wp:paragraph -->

<!-- wp:columns -->
<div class="wp-block-columns"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph -->
<p>[su_note note_color="#fdfcdc" text_color="#0081a7" class="mynote"]</p>
<!-- /wp:paragraph -->

<!-- wp:list ###"ordered":true*** -->
<ol id="index-table"><!-- wp:list-item -->
<li><a href="#esc1">{results[0]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc2">{results[1]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc3">{results[2]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc4">{results[3]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc5">{results[4]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc6">{results[5]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc7">{results[6]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc8">{results[7]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc8">{results[8]["Nombre"]}</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc8">{results[9]["Nombre"]}</a></li>
<!-- /wp:list-item --></ol>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>[/su_note]</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column ###"verticalAlignment":"center"*** -->
<div class="wp-block-column is-vertically-aligned-center"><!-- wp:image ###"align":"center","id":9,"width":"277px","height":"auto","sizeSlug":"medium","linkDestination":"none"*** -->
<figure class="wp-block-image aligncenter size-medium is-resized"><img src="https://educalia.us/wp-content/uploads/2024/01/Educalia-300x263.png" alt="{search} en {city}" class="wp-image-9" style="width:277px;height:auto"/></figure>
<!-- /wp:image --></div>
<!-- /wp:column --></div>
<!-- /wp:columns -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[0]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[0]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[0]["Nombre"]}</h2>
            <p class="text-description">{results[0]["Descripcion"]}</p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[0]["Telefono"]}"><b>{results[0]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[0]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[0]["Direccion"]}</p>
            <div class="footer-section">
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[1]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[1]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[1]["Nombre"]}</h2>
            <p class="text-description">{results[1]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[1]["Telefono"]}"><b>{results[1]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[1]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[1]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>1.640</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[2]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[2]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[2]["Nombre"]}</h2>
            <p class="text-description">{results[2]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[2]["Telefono"]}"><b>{results[2]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[2]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[2]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>209</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privado</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[3]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[3]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[3]["Nombre"]}</h2>
            <p class="text-description">{results[3]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[3]["Telefono"]}"><b>{results[3]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[3]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[3]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>3.929</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[4]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[4]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[4]["Nombre"]}</h2>
            <p class="text-description">{results[4]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[4]["Telefono"]}"><b>{results[4]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[4]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[4]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>2.073</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[5]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[5]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[5]["Nombre"]}</h2>
            <p class="text-description">{results[5]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[5]["Telefono"]}"><b>{results[5]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[5]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[5]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>600</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[6]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[6]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[6]["Nombre"]}</h2>
            <p class="text-description">{results[6]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[6]["Telefono"]}"><b>{results[6]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[6]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[6]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>400</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[7]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[7]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[7]["Nombre"]}</h2>
            <p class="text-description">{results[7]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[7]["Telefono"]}"><b>{results[7]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[7]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[7]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>289</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[8]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[8]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[8]["Nombre"]}</h2>
            <p class="text-description">{results[8]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[8]["Telefono"]}"><b>{results[8]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[8]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[8]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>173</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Hispana</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url({results[9]["Foto"]});"></div>
            <div class="map-container">
                <iframe src="{results[9]["Enlace para Iframe"]}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>{results[9]["Nombre"]}</h2>
            <p class="text-description">{results[9]["Descripcion"]}</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:{results[9]["Telefono"]}"><b>{results[9]["Telefono"]}</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> {results[9]["Sitio Web"]}/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp{results[9]["Direccion"]}</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>289</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:heading ###"textAlign":"center"*** -->
<h2 class="wp-block-heading has-text-align-center">Preguntas frecuentes sobre {search}</h2>
<!-- /wp:heading -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Cómo puedo encontrar {search} cerca de mí en áreas como {city}?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para encontrar {search} cerca, puedes utilizar herramientas de búsqueda en línea específicas para tu localidad, como mapas interactivos y directorios escolares locales. También es útil visitar los sitios web  para obtener listados y detalles adicionales sobre las opciones disponibles en tu área.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué diferencia hay entre middle school y high school?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>En {country}, el sistema educativo se divide en varias etapas, siendo el middle school (que generalmente abarca de 6º a 8º grado) la etapa intermedia entre la escuela primaria y la high school (secundaria, que cubre de 9º a 12º grado). Cada nivel se enfoca en preparar a los estudiantes para la siguiente etapa educativa, con el middle school centrado en la transición de la niñez a la adolescencia y el high school preparando a los estudiantes para la educación superior o carreras técnicas.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué son las {search} y cómo se comparan con las {search} tradicionales?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las {search} técnicas ofrecen programas especializados que preparan a los estudiantes para carreras específicas a través de cursos prácticos y teóricos en campos como tecnología, salud y mecánica. A diferencia de las {search} tradicionales, que proporcionan una educación más general, las técnicas permiten a los estudiantes adquirir habilidades prácticas y experiencia en áreas de interés específicas.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué beneficios ofrece una {search} pública frente a una privada?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las {search} públicas suelen ofrecer educación sin costo de matrícula, financiada por impuestos locales y estatales, y reflejan la diversidad de su comunidad. Por otro lado, las {search} privadas pueden ofrecer programas especializados y ratios más bajos de estudiantes por docente, pero generalmente requieren el pago de matrícula.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Existen programas bilingües en las {search} de ciudades como {city}?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Sí, muchas {search} ofrecen programas bilingües que buscan fortalecer las habilidades lingüísticas en inglés y otro idioma, como el español. Estos programas están diseñados para mejorar la fluidez y comprensión cultural, preparándolos para un mundo cada vez más globalizado.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Cómo puedo elegir la mejor {search}?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Elegir la mejor {search} implica considerar varios factores. Es recomendable visitar las {search} de interés, hablar con personas relacioandas, y revisar las evaluaciones y rankings.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué importancia tienen las actividades extracurriculares?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las actividades extracurriculares juegan un papel crucial en el desarrollo integral, permitiéndo explorar intereses fuera del currículo académico, desarrollar habilidades sociales y de liderazgo, y mejorar su bienestar emocional.</p>
<!-- /wp:paragraph -->
</body>
        '''
        html_fresh = html_content.replace("###","{").replace("***","}")
        with open(f'Pantilla_{city}.html', 'w', encoding='utf-8') as file:
            file.write(html_fresh)
        print(f" ---> HTML GENERADO CORRECTAMENTE --> 'Plantilla_{city}.html' ")

#---FIN-SECTOR-PLANTILLA---------------------------------------------------------------------------#

#---INICIO-SECTOR-PLANTILLA-CON-VARIABLE-TIPO-$VARIABLE--------------------------------------------#

        html_content_variable_dollar = f'''
        
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Las Mejores {search} en {city}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<!-- wp:html -->
<h1 class="heading">Las Mejores <span class="underline--magical">{search} en {city} </span> </h1>
<!-- /wp:html -->

<!-- wp:paragraph -->
<p>{description_city} </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{introductory_text}</p>
<!-- /wp:paragraph -->

<!-- wp:columns -->
<div class="wp-block-columns"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph -->
<p>[su_note note_color="#fdfcdc" text_color="#0081a7" class="mynote"]</p>
<!-- /wp:paragraph -->

<!-- wp:list ###"ordered":true*** -->
<ol id="index-table"><!-- wp:list-item -->
<li><a href="#esc1">$CIUDAD_0</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc2">$CIUDAD_1</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc3">$CIUDAD_2</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc4">$CIUDAD_3</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc5">$CIUDAD_4</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc6">$CIUDAD_5</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc7">$CIUDAD_6</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc8">$CIUDAD_7</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc8">$CIUDAD_8</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="#esc8">$CIUDAD_9</a></li>
<!-- /wp:list-item --></ol>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>[/su_note]</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column ###"verticalAlignment":"center"*** -->
<div class="wp-block-column is-vertically-aligned-center"><!-- wp:image ###"align":"center","id":9,"width":"277px","height":"auto","sizeSlug":"medium","linkDestination":"none"*** -->
<figure class="wp-block-image aligncenter size-medium is-resized"><img src="https://educalia.us/wp-content/uploads/2024/01/Educalia-300x263.png" alt="{search} en {city}" class="wp-image-9" style="width:277px;height:auto"/></figure>
<!-- /wp:image --></div>
<!-- /wp:column --></div>
<!-- /wp:columns -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_0);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_0" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_0</h2>
            <p class="text-description">$DESCRIPCION_0</p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_0"><b>$TELEFONO_0</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_0/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_0</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>1.640</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_1);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_1" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_1</h2>
            <p class="text-description">$DESCRIPCION_1</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_1"><b>$TELEFONO_1</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_1/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_1</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>1.640</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_2);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_2" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_2</h2>
            <p class="text-description">$DESCRIPCION_2</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_2"><b>$TELEFONO_2</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_2/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_2</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>209</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privado</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_3);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_3" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_3</h2>
            <p class="text-description">$DESCRIPCION_3</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_3"><b>$TELEFONO_3</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_3/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_3</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>3.929</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_4);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_4" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_4</h2>
            <p class="text-description">$DESCRIPCION_4</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_4"><b>$TELEFONO_4</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_4/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_4</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>2.073</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_5);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_5" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_5</h2>
            <p class="text-description">$DESCRIPCION_5</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_5"><b>$TELEFONO_5</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_5/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_5</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>600</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_6);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_6" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_6</h2>
            <p class="text-description">$DESCRIPCION_6</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_6"><b>$TELEFONO_6</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_6/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_6</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>400</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_7);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_7" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_7</h2>
            <p class="text-description">$DESCRIPCION_7</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_7"><b>$TELEFONO_7</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_7/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_7</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>289</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_8);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_8" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_8</h2>
            <p class="text-description">$DESCRIPCION_8</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_8"><b>$TELEFONO_8</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_8/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_8</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>173</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Publica</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Hispana</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:html -->
<div class="info-panel">
        <div class="image-section">
            <div class="image-container" style="background-image: url($FOTO_9);"></div>
            <div class="map-container">
                <iframe src="$IFRAME_9" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="content-section">
            <h2>$CIUDAD_9</h2>
            <p class="text-description">$DESCRIPCION_9</p>
            <p></p>
            <div class="contact-details">
                <p class="detail-item"><b>Telefono:&nbsp</b> <a href="TEL:$TELEFONO_9"><b>$TELEFONO_9</b></a></p>
                <p class="detail-item"><b>Web:&nbsp</b> $WEBSITE_9/</p>
                <p class="detail-item"><b>Dirección:</b> &nbsp$DIRECCION_9</p>
                <p class="detail-item"><b>Nº de estudiantes:&nbsp;</b>289</p>
            </div>
            <div class="amenities">
            <span class="amenity-icon">Privada</span>
            <span class="amenity-icon">Mixto</span>
            <span class="amenity-icon">Bilingüe</span>
            </div>
            <div class="footer-section">
                
                <button><a href="https://educalia.com/#reservar">Reserva ahora</a></button>
            </div>
        </div>
    </div>
<!-- /wp:html -->

<!-- wp:spacer ###"height":"34px"*** -->
<div style="height:34px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:heading ###"textAlign":"center"*** -->
<h2 class="wp-block-heading has-text-align-center">Preguntas frecuentes sobre {search}</h2>
<!-- /wp:heading -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Cómo puedo encontrar {search} cerca de mí en áreas como {city}?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para encontrar {search} cerca, puedes utilizar herramientas de búsqueda en línea específicas para tu localidad, como mapas interactivos y directorios escolares locales. También es útil visitar los sitios web  para obtener listados y detalles adicionales sobre las opciones disponibles en tu área.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué diferencia hay entre middle school y high school?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>En {country}, el sistema educativo se divide en varias etapas, siendo el middle school (que generalmente abarca de 6º a 8º grado) la etapa intermedia entre la escuela primaria y la high school (secundaria, que cubre de 9º a 12º grado). Cada nivel se enfoca en preparar a los estudiantes para la siguiente etapa educativa, con el middle school centrado en la transición de la niñez a la adolescencia y el high school preparando a los estudiantes para la educación superior o carreras técnicas.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué son las {search} y cómo se comparan con las {search} tradicionales?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las {search} técnicas ofrecen programas especializados que preparan a los estudiantes para carreras específicas a través de cursos prácticos y teóricos en campos como tecnología, salud y mecánica. A diferencia de las {search} tradicionales, que proporcionan una educación más general, las técnicas permiten a los estudiantes adquirir habilidades prácticas y experiencia en áreas de interés específicas.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué beneficios ofrece una {search} pública frente a una privada?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las {search} públicas suelen ofrecer educación sin costo de matrícula, financiada por impuestos locales y estatales, y reflejan la diversidad de su comunidad. Por otro lado, las {search} privadas pueden ofrecer programas especializados y ratios más bajos de estudiantes por docente, pero generalmente requieren el pago de matrícula.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Existen programas bilingües en las {search} de ciudades como {city}?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Sí, muchas {search} ofrecen programas bilingües que buscan fortalecer las habilidades lingüísticas en inglés y otro idioma, como el español. Estos programas están diseñados para mejorar la fluidez y comprensión cultural, preparándolos para un mundo cada vez más globalizado.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Cómo puedo elegir la mejor {search}?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Elegir la mejor {search} implica considerar varios factores. Es recomendable visitar las {search} de interés, hablar con personas relacioandas, y revisar las evaluaciones y rankings.</p>
<!-- /wp:paragraph -->

<!-- wp:heading ###"level":3*** -->
<h3 class="wp-block-heading">¿Qué importancia tienen las actividades extracurriculares?</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las actividades extracurriculares juegan un papel crucial en el desarrollo integral, permitiéndo explorar intereses fuera del currículo académico, desarrollar habilidades sociales y de liderazgo, y mejorar su bienestar emocional.</p>
<!-- /wp:paragraph -->
</body>
        '''
        html_fresh = html_content_variable_dollar.replace("###","{").replace("***","}")
        with open(f'Plantilla_{city}_variable_dollar.html', 'w', encoding='utf-8') as file:
            file.write(html_fresh)
        print(f" ---> HTML CON VARIABLE '$' GENERADO CORRECTAMENTE --> 'Plantilla_{city}_variable_dollar.html' ")
#---FIN-SECTOR-PLANTILLA-CON-VARIABLE-TIPO-$VARIABLE-----------------------------------------------#
    else:
        print(f" ---> ERROR AL INICAR LA CONEXION:", response.status_code)  
    return results        
    
####################################################################################################        

def main():
    if len(sys.argv) != 3:
        animation = 0.05
        print(f"  .--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--.  ")
        time.sleep(animation)
        print(f" / .. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\ ")
        time.sleep(animation)
        print(f" \\ \\/\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ \\/ / ")
        time.sleep(animation)
        print(f"  \\/ /`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\\/ /  ")
        time.sleep(animation)
        print(f"  / /\\                                                                                            / /\\  ")
        time.sleep(animation)
        print(f" / /\\ \\                                                                                          / /\\ \\ ")
        time.sleep(animation)
        print(f" \\ \\/ /     █████████  ██████████ ███████████    █████ ██████   █████ ███████████    ███████     \\ \\/ / ")
        time.sleep(animation)
        print(f"  \\/ /     ███░░░░░███░░███░░░░░█░█░░░███░░░█   ░░███ ░░██████ ░░███ ░░███░░░░░░█  ███░░░░░███    \\/ /  ")
        time.sleep(animation)
        print(f"  / /\\    ███     ░░░  ░███  █ ░ ░   ░███  ░     ░███  ░███░███ ░███  ░███   █ ░  ███     ░░███   / /\\  ")
        time.sleep(animation)
        print(f" / /\\ \\  ░███          ░██████       ░███        ░███  ░███░░███░███  ░███████   ░███      ░███  / /\\ \\ ")
        time.sleep(animation)
        print(f" \\ \\/ /  ░███    █████ ░███░░█       ░███        ░███  ░███ ░░██████  ░███░░░█   ░███      ░███  \\ \\/ / ")
        time.sleep(animation)
        print(f"  \\/ /   ░░███  ░░███  ░███ ░   █    ░███        ░███  ░███  ░░█████  ░███  ░    ░░███     ███    \\/ /  ")
        time.sleep(animation)
        print(f"  / /\\    ░░█████████  ██████████    █████       █████ █████  ░░█████ █████       ░░░███████░     / /\\  ")
        time.sleep(animation)
        print(f" / /\\ \\    ░░░░░░░░░  ░░░░░░░░░░    ░░░░░       ░░░░░ ░░░░░    ░░░░░ ░░░░░          ░░░░░░░      / /\\ \\ ")
        time.sleep(animation)
        print(f" \\ \\/ /                                                                                          \\ \\/ / ")
        time.sleep(animation)
        print(f"  \\/ /  Version: 1.5.1 Release -------------------------------- © Todos los derechos reservados.  \\/ /  ")
        time.sleep(animation)
        print(f"  / /\\.--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--./ /\\  ")
        time.sleep(animation)
        print(f" / /\\ \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\.. \\/\\ \\ ")
        time.sleep(animation)
        print(f" \\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `'\\ `' / ")
        time.sleep(animation)
        print(f"  `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'  \\n")
        time.sleep(animation)
        print(f"\\nUso: python3 GET-INFO_API_v1.5.1.py archivo_ciudades.txt <-Que buscas/Busqueda->\\n")
        time.sleep(animation)
        print(f"Ejemplo: python3 GET-INFO_API_v1.5.1.py Ciudades_España.txt Restaurantes+Vegetarianos\\n")
        time.sleep(animation)
        print(f"Este script obtiene informacion relevante, genera informacion adicional y exporta los datos.")
        time.sleep(animation)
        print(f"--> Lee un archivo de ciudades organzado en pares 'Ciudad, Pais' por cada linea ")
        time.sleep(animation)
        print(f"--> Hace consultas de automatizadas a Google Map con base en los parametros:")
        time.sleep(animation)
        print(f"----> 'Busqueda' => (Argumeto ingresado de ejecucion)")
        time.sleep(animation)
        print(f"----> 'Ciudad'   => Extraido del archivo")
        time.sleep(animation)
        print(f"----> 'Pais'     => Extraido del archivo")
        time.sleep(animation)        
        print(f"------> Para mas de UNA palabra en el argumento 'Busqueda' separar por el caracter '+' ")
        time.sleep(animation)
        print(f"--> Con base en los datos adquiridos conecta con OpenAI, analiza y genera informacion adicional.")
        time.sleep(animation)
        print(f"--> Exporta la informacion en archivos CSV con los datos de 10 sitios por cada ciudad.")
        time.sleep(animation)
        print(f"--> Genera 2 plantillas HTML con base en formatos preestablecidos.")
        sys.exit(1)

    archivo_ciudades = sys.argv[1]
    search = sys.argv[2]

    with open(archivo_ciudades, "r") as file:
        for line in file:
            city, country = line.strip().split(",", 1)
            city = city.strip().replace(" ", "+").upper()
            country = country.strip().replace(" ", "+").upper()
            print(f"\n ===> EJECUTANDO GET_INFO_API_v1.5.0 CON '{search}' EN {city}, {country}")
            get_info(search, city, country)

if __name__ == "__main__":
    main()
