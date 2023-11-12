#!/usr/bin/env python3
import datetime
import sqlite3
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image
import PIL.ImageOps


def getDataRows(dbfile):
	dataRows = []
	try:
		con = sqlite3.connect(dbfile)
		cursor = con.cursor()
		query = "SELECT * from tempHist2"
		cursor.execute(query)
		records = cursor.fetchall()
		for row in records:
			row = list(row)
			row[0] = datetime.datetime.fromtimestamp(row[0])
			dataRows.append(row)

		cursor.close()

	except sqlite3.Error as error:
		print("Failed to read data from sqlite table", error)
	finally:
		if con:
			con.close()
	dataRows = pd.DataFrame(dataRows,columns=["Date","Nicci's Room","Terry's Room","Living Room"])
	return dataRows

df = getDataRows('temphist.sqlite3')
ax = df.plot(x='Date',kind='line')
ax.set_ylabel('Temperature')
fig = plt.gcf()
plt.draw()
fig.savefig('histwhite.jpg')

image = Image.open('histwhite.jpg')
inverted_image = PIL.ImageOps.invert(image)
inverted_image.save('histblack.jpg')
```
---


<small>This page, images and code are Copyright &copy; 2023 [Nicole Stevens](/sensorfs/about.html) All rights reserved.</small>
