import folium

m = folium.Map(location=[-5, -38],zoom_start=8)
folium.GeoJson('./viz/latest-2-month.geojson',name='geojson',tooltip=folium.features.GeoJsonTooltip(fields=['id_jrc'],aliases=['ID'],labels=True,localize=True,sticky=True)).add_to(m)
folium.LayerControl().add_to(m)
m.save('index.html')
