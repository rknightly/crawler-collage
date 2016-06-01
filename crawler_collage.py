import urllib.request
import urllib.parse
from urllib import request, parse
from bs4 import BeautifulSoup


class UserInput:
    """Get the page to crawl from the user"""

    def __init__(self):
        self.user_url = ""
        self.user_page_num = 0

        self.find_user_url()
        self.find_user_page_num()

    def find_user_url(self):
        user_url = input("Start page -> ")
        if user_url == "":
            user_url = "https://cnn.com"

        self.user_url = user_url

    def find_user_page_num(self):
        user_page_num = input("Pages to crawl -> ")
        if user_page_num.is_digit():
            user_page_num = int(user_page_num)
        else:
            user_page_num = 5
        self.user_page_num = user_page_num

    def get_user_url(self):
        return self.user_url

    def get_user_page_num(self):
        return self.user_page_num


class Crawler:
    """Visit the web pages and collect the necessary information"""

    def __init__(self, user_settings):
        self.settings = user_settings
        self.initial_page = self.settings.get_user_url()
        self.pages_to_visit = self.settings.get_user_page_num()

    def visit_page(self):
        pass


class Page:
    """Store the information of a single page"""
    def __init__(self, url):
        self.url = url
        self.links = []

    def collect_links(self):
        """Collect all links from a page"""
        page_request = request.Request(self.url)
        response = request.urlopen(page_request)
        soup = BeautifulSoup(response, "lxml")  # Specify the parser to use

        # Grab all of the links with BeautifulSoup and only keep the ones with
        # "www." to ensure that self-referencing links are not collected
        links = set([link['href'] for link in soup.findAll('a') if
                     "www." in link['href']])

        self.links.extend(links)

        return links

    def collect_images(self, page_url):
        """Collect all of the images on the page and save them to a folder"""
        page_request = urllib.request.Request(page_url)
        response = urllib.request.urlopen(page_request)
        soup = BeautifulSoup(response, "lxml")  # Specify the parser to use

        unnamed_images = 0

        for img in soup.findAll('img'):
            temp = img.get('src')

            image_url = self.verify_abs_url(page_url=page_url,
                                            img_url=temp)

            name_temp = img.get("alt")
            # Deal with missing alt text
            if len(name_temp) == 0:
                file_name = "img_" + str(unnamed_images)
                unnamed_images += 1
            else:
                file_name = name_temp
            print(image_url)
            image_file = open("../images/" + file_name + ".jpeg", "wb")
            image_file.write(urllib.request.urlopen(image_url).read())
            image_file.close()

    def verify_abs_url(self, img_url):
        """Take an image url and if it is not an absolute url, make it one and
        return it
        """

        new_img_url = img_url

        if img_url[:2] == "//":
            print("It happened")
            new_img_url = "http:" + img_url
        elif img_url[:1] == "/":
            new_img_url = self.url + img_url
        else:
            new_img_url = img_url

        return new_img_url


class ImageData:
    def __init__(self, image_url, alt_text):
        self.image_url = image_url
        self.alt_text = alt_text

    def get_image_url(self):
        return self.image_url

    def get_alt_text(self):
        return self.alt_text


class ImageDowloader:
    """Download the images at the given url"""

    def __init__(self, img_object):
        self.img = img_object

    def clear_folder(self):
        pass

    def download_images(self):
        pass


class Program:
    """Run the main program"""

    def __init__(self):
        self.user_input = UserInput()
        self.crawler = Crawler(self.user_input)


# Visit page

        # Store in folder

    # Collect links

        # Store in list

# Visit the stored links until level num reached. Or

    # page num reached, or level num reached

# Create new image with collected images

    # Make the background with the first image

    # Place other photos

        # Add at random angle and size

        # Save result

# Display saved result
