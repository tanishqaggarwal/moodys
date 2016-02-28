import math, geopy, geopy.distance 
from geopy.distance import vincenty

counties = []

tmean = 0
dmean = 0
outfile = open("distance-time-pairs-2.csv", "w")

i = 0

with open("enjoy.txt") as f:
	for line in f:
		line       = line.rstrip("\n").split()
		newline = []
		for element in line:
			if not any(x not in ["0","1","2","3","4","5","6","7","8","9",",",".","-"] for x in element):
				newline.append(element.replace(",",""))

		line = newline
		fips       = line[1]
		population = int(line[2])
		area       = float(line[4]) #sq mi
		latitude   = float(line[9])
		longitude  = float(line[10])

		sidelength = math.sqrt(area)
		density = population / area
		classification = 0 #50 is rural, 35 is suburban, 25 is urban
		if density < 500:
			classification = 55 #rural
		elif density < 1000:
			classification = 42.5 #suburban
		else:
			classification = 25 #urban

		counties.append((fips, [classification, sidelength, (latitude, longitude)]))

counties = dict(counties)

lines = []

with open("2009data.csv") as f:
	for line in f:
		lines.append(line)

for line in lines:
	line = line.rstrip("\r\n").split(",")
	fips1 = line[0] + line[1]
	fips2 = line[2] + line[3]
	fips2 = fips2[1:]

	flow = None
	if len(line) != 5:
		flow = int(line[-2][1:] + line[-1][:-1])
	else:
		flow = int(line[-1])

	try:
		county1 = counties[fips1]
		county2 = counties[fips2]
	except:
		continue

	distance = vincenty(county1[2], county2[2]).miles		
	time = (distance - county1[1] * 0.5611 - county2[1] * 0.5611) / 65 + county1[1] / county1[0] * 0.5611 + county2[1] * 0.5611 / county2[0] #for faraway counties
	if distance < math.sqrt(2) * (county1[1] + county2[1]) / 2: 
		ratio1 = county1[1] / (county1[1] + county2[1])
		ratio2 = county2[1] / (county1[1] + county2[1])
		distance = 0.5214 * distance
		time = distance * (ratio1 / county1[0] + ratio2 / county2[0])
		if distance < 0.001:
			distance = 0.5214 * county1[1]
			time = distance / county1[0]

	for x in range(0, flow):
		i += 1
		dmean = (dmean * (i - 1) + distance) / i;
		tmean = (tmean * (i - 1) + time) / i;
		if i % 10000 == 0:
			outfile.write(str(time) + "," + str(distance) + "\n");

outfile.close()
f.close()

print dmean
print tmean