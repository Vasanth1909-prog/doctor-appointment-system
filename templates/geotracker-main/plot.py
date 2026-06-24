import folium 
map = folium.Map(location=[12.942070, 79.196545], zoom_start=13)
folium.Marker([12.942070, 79.196545], popup='example location').add_to(map)
map.save("./map.html")