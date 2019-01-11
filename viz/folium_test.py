import folium

m = folium.Map([60, 10], tiles='Mapbox Bright', zoom_start=5)
folium.Circle([60, 10], 150000, fill=True).add_child(folium.Popup('My name is Circle')).add_to(m)

m.save('test.html')
