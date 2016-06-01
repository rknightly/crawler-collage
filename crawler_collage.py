import urllib.request
import urllib.parse
from urllib import request
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import random


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
        if user_page_num.isdigit():
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
        self.url_base = self.get_url_base()
        self.links = self.collect_links()
        self.images = self.collect_images()

    def get_url_base(self):
        url_parts = urlparse(self.url)
        main_website_url = url_parts.scheme + "://" + url_parts.netloc
        return main_website_url

    def collect_links(self):
        """Collect all links from a page"""
        page_request = request.Request(self.url)
        response = request.urlopen(page_request)
        soup = BeautifulSoup(response, "lxml")  # Specify the parser to use

        # Grab all of the links with BeautifulSoup and only keep the ones with
        # "www." to ensure that self-referencing links are not collected
        # links = {link['href'] for link in soup.findAll('a')}

        links = set()
        for link in soup.findAll('a'):
            try:
                links.add(link['href'])
            except KeyError:
                pass

        abs_links = {self.verify_abs_url(test_url=link) for link in links}

        return abs_links

    def collect_images(self):
        """Collect all of the images on the page and save them to a folder"""
        page_request = urllib.request.Request(self.url)
        response = urllib.request.urlopen(page_request)
        soup = BeautifulSoup(response, "lxml")  # Specify the parser to use

        unnamed_images = 0
        images = set()

        for img in soup.findAll('img'):
            temp = img.get('src')

            image_url = self.verify_abs_url(test_url=temp)
            image_alt_text = img.get("alt")
            image = ImageData(image_url=image_url, alt_text=image_alt_text)
            images.add(image)

        return images

    def verify_abs_url(self, test_url):
        """Take an image url and if it is not an absolute url, make it one and
        return it
        """

        abs_img_url = urljoin(self.get_url_base(), test_url)

        return abs_img_url

    def get_links(self):
        return self.links

    def get_images(self):
        return self.images


class ImageData:
    def __init__(self, image_url, alt_text):
        self.image_url = image_url
        self.alt_text = alt_text
        self.file_name = self.make_name()
        print(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return id(self)

    def make_name(self):
        file_name = self.alt_text
        # Deal with missing alt text
        if len(file_name) == 0:
            file_name = "unnamed_img_" + str(random.randrange(10000))

        return file_name

    def get_image_url(self):
        return self.image_url

    def get_alt_text(self):
        return self.alt_text

    def get_file_name(self):
        return self.file_name


class ImageDownloader:
    """Download the images at the given url"""

    def __init__(self, img_objects):
        self.imgs = img_objects

    def clear_folder(self):
        pass

    def download_images(self):
        for img in self.imgs:
            image_file = open("../images/" + img.get_file_name + ".jpeg", "wb")
            image_file.write(urllib.request.urlopen(img.get_image_url())
                             .read())
            image_file.close()


class Program:
    """Run the main program"""

    def __init__(self):
        self.user_input = UserInput()
        self.crawler = Crawler(self.user_input)

if __name__ == "__main__":
    program = Program()


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
