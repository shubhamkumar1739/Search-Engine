from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome("/home/ironman/chromedriver")
driver.get("https://www.hindisahityadarpan.in/2015/12/inspirational-hindi-stories-collection.html")

page = BeautifulSoup(driver.page_source, "html")

links = page.find_all("ol", {"style" : "font-family: \"vesper libre medium\"; margin-bottom: 0in; margin-left: 0.375in; margin-top: 0in; text-align: left; unicode-bidi: embed;"})

story_count = 0
for link in links : 

	sublist = link.find_all("a")
	for item in sublist :
		lk = str(item["href"])

		driver.get(lk)

		story = BeautifulSoup(driver.page_source, "html")

		story_str = ""
		title = ""

		paras = story.find("div", {"class" : "post-body-inner"})

		story_str = paras.text

		story_count += 1
		#add to file
		filename = "Files/" + str(story_count) + ".txt"
		with open(filename, "w+") as file :
			file.write(story_str)
			file.close()

