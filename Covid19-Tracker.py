import requests
from bs4 import BeautifulSoup

import pandas as pd
import plotly.express as px
import json

from datetime import date

def prepareData(url, geoJson):
	print("Grabbing Data...")

	page = requests.get(url, verify=False)
	html = BeautifulSoup(page.content, 'html.parser')
	table = html.find(summary="Texas COVID-19 Cases")

	data = []
	rows = table.find_all("tr")
	dataFile = open("texas_covid_19.csv", "w")
	dataFile.write("fips,County,Cases")

	counties = dict()

	for county in geoJson["features"]:
		counties[county["properties"]["NAME"]] = county["id"]

	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		if len(cols) != 0:
			cols[0] = str(cols[0])
			cols[1] = int(cols[1])
			if cols[0] != "Total":
				data.append([ele for ele in cols if ele])
				dataFile.write("\n" + counties[cols[0]] + "," + cols[0] + "," + str(cols[1]))

	for county in counties:
		if not any(county in i for i in data):
			dataFile.write("\n" + counties[county] + "," + county + ",0")

	print("Data Collected:")
	print(data)
	return data


def drawFigure(geoJson, maxRange):
	df = pd.read_csv("texas_covid_19.csv", dtype={"fips": str})

	fig = px.choropleth(df, geojson=geoJson, locations='fips', color='Cases',
						color_continuous_scale="reds",
						range_color=(0, maxRange),
						scope="usa",
						hover_data=["County", "Cases"]
						)
	fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
	fig.update_geos(fitbounds="locations")
	return fig

def main():
	texas = json.load(open("texas.json"))
	data = prepareData(geoJson=texas, url="https://dshs.texas.gov/news/updates.shtm#coronavirus")
	figure = drawFigure(geoJson=texas, maxRange=max(data, key=lambda x: x[1])[1])
	figure.show()

	output = "tracking/" + str(date.today().strftime("%d-%m-%Y")) +".html"
	print("Writing to file: " + output)
	figure.write_html(output)

main()
