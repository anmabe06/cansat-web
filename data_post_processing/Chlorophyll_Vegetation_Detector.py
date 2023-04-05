import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import math

from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import cv2
import extcolors

from colormap import rgb2hex


class Chlorophyll_Vegetation_Detector():
	def __init__(self, input_image_name: str = "", input_image_path: str = "", resize: int = 900, tolerance: int = 12, zoom: float = 2.5, colour_mode = "HEX"):
		self.input_image_name = input_image_name
		self.input_image_path = input_image_path
		self.resize = resize
		self.tolerance = tolerance
		self.zoom = zoom
		self.colour_mode = colour_mode

  
	def extract_colours(self):
		#background
		bg = 'bg.png'
		fig, ax = plt.subplots(figsize=(192,108),dpi=10)
		fig.set_facecolor('white')
		plt.savefig(bg)
		plt.close(fig)
		
		#resize
		output_width = self.resize
		img = Image.open(self.input_image_path + self.input_image_name)
		if img.size[0] >= self.resize:
			wpercent = (output_width/float(img.size[0]))
			hsize = int((float(img.size[1])*float(wpercent)))
			img = img.resize((output_width,hsize), Image.ANTIALIAS)
			self.resize_name = 'resize_'+ self.input_image_name
			img.save(self.resize_name)
		else:
			self.resize_name = self.input_image_name
      
		#crate dataframe
		img_url = self.input_image_path + self.resize_name
		colors_x = extcolors.extract_from_path(img_url, tolerance = self.tolerance, limit = 13)
		df_color = self.color_to_df(colors_x)
      
		#annotate text
		self.list_colour = list(df_color['c_code'])
		
		if self.colour_mode == "RGB":
			self.list_colour_rgb = []
			for colour in self.list_colour:
				self.list_colour_rgb.append(self.hex_to_rgb(colour))

		
		self.list_percent = [int(i) for i in list(df_color['occurence'])]
		self.list_percent = list(np.round(np.array(self.list_percent) * 100 /sum(self.list_percent), 2))

	
	def get_percentage_of_green(self):
		if self.colour_mode != "RGB":
			raise Exception("Parameter 'colour_mode' must be set to RGB in order to perform this action")
		
		total_percent = 0
		
		base_green = np.array([0, 255, 0])

		for c, p in zip(self.list_colour_rgb, self.list_percent):
			colour = np.array(c)

			# Calculate Eucledian distance to see the deviation from green (must be below 200)
			if np.linalg.norm(base_green - colour) < 200:
				# print(p)
				total_percent += p

			# Contemplate very dark greens
			elif c[1] - 10 >= c[0] and c[1] - 10 >= c[2]:
				# print(p)
				total_percent += p

		
		print(f"\033[92mPercentage of vegetation: {total_percent}%\033[0m")
		
		return total_percent

  
	def color_to_df(self, input):
		colors_pre_list = str(input).replace('([(','').split(', (')[0:-1]
		df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
		df_percent = [i.split('), ')[1].replace(')','') for i in colors_pre_list]

		#convert RGB to HEX code
		df_color_up = [rgb2hex(int(i.split(", ")[0].replace("(","")),
								int(i.split(", ")[1]),
								int(i.split(", ")[2].replace(")",""))) for i in df_rgb]

		df = pd.DataFrame(zip(df_color_up, df_percent), columns = ['c_code','occurence'])
		return df
	

	def hex_to_rgb(self, hex_value):
		hex_value = hex_value.lstrip("#")
		return list(int(hex_value[i:i+2], 16) for i in (0, 2, 4))


	def show_colours_in_console(self):
		if self.colour_mode == "RGB":
			for c1, c2, p in zip(self.list_colour, self.list_colour_rgb, self.list_percent):
				print(f'{c1}/{c2}: {p}%')
		else:
			for c, p in zip(self.list_colour, self.list_percent):
				print(f'{c}: {p}%')


  
	def show_colours_in_screen(self):
		text_c = [c + ' ' + str(p) +'%' for c, p in zip(self.list_colour, self.list_percent)]
		
		fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(160,120), dpi = 10)
      
		#donut plot
		wedges, text = ax1.pie(self.list_percent,
								labels= text_c,
								labeldistance= 1.05,
								colors = self.list_colour,
								textprops={'fontsize': 150, 'color':'black'})
		plt.setp(wedges, width=0.3)

		#add image in the center of donut plot
		img = mpimg.imread(self.input_image_path + self.resize_name)
		imagebox = OffsetImage(img, zoom=self.zoom)
		ab = AnnotationBbox(imagebox, (0, 0))
		ax1.add_artist(ab)
		
		#color palette
		x_posi, y_posi, y_posi2 = 160, -170, -170
		for c in self.list_colour:
			if self.list_colour.index(c) <= 5:
				y_posi += 180
				rect = patches.Rectangle((x_posi, y_posi), 360, 160, facecolor = c)
				ax2.add_patch(rect)
				ax2.text(x = x_posi+400, y = y_posi+100, s = c, fontdict={'fontsize': 190})
			else:
				y_posi2 += 180
				rect = patches.Rectangle((x_posi + 1000, y_posi2), 360, 160, facecolor = c)
				ax2.add_artist(rect)
				ax2.text(x = x_posi+1400, y = y_posi2+100, s = c, fontdict={'fontsize': 190})

		fig.set_facecolor('white')
		ax2.axis('off')
		bg = plt.imread('bg.png')
		plt.imshow(bg)       
		plt.tight_layout()
		return plt.show()
    

if __name__ == "__main__":
	Chlorophyll_Vegetation_Detector = Chlorophyll_Vegetation_Detector(input_image_name='asdf2.jpeg', input_image_path='/Users/anmabe06/Desktop/', colour_mode="RGB")
	Chlorophyll_Vegetation_Detector.extract_colours()
	Chlorophyll_Vegetation_Detector.get_percentage_of_green()
	# Chlorophyll_Vegetation_Detector.show_colours_in_console()
	#Chlorophyll_Vegetation_Detector.show_colours_in_screen()