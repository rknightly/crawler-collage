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
        self.user_page_lim = 0

    def find_user_url(self):
        """Get the url to start on from the user"""

        user_url = input("Start page -> ")
        if user_url == "":
            user_url = "https://cnn.com"

        self.user_url = user_url

    def find_user_page_num(self):
        """Get the max number of pages that will be visited"""

        user_page_num = input("Pages to crawl -> ")
        if user_page_num.isdigit():
            user_page_num = int(user_page_num)
        else:
            user_page_num = 5
        self.user_page_lim = user_page_num

    def request_user_settings(self):
        """Get both the starting url and max number of pages from the user"""

        self.find_user_url()
        self.find_user_page_num()

    def get_user_url(self):
        """Return the initial url"""

        return self.user_url

    def get_user_page_lim(self):
        """Return the max number of pages to be crawled"""

        return self.user_page_lim


class Crawler:
    """Visit the web pages and collect the necessary information"""

    def __init__(self, user_settings):
        self.settings = user_settings
        self.initial_page = self.settings.get_user_url()
        self.pages_to_visit = self.settings.get_user_page_lim()

        # Initialise the collection of links to visit with the initial link
        # given by the user.
        self.links_to_visit = set(self.settings.get_user_url)
        self.images = set()

    def visit_page(self, url):
        """Run the processes necessary upon visitation of a single page"""

        page = Page(url)
        self.dump_data(page)

    def dump_data(self, page):
        """
        Take the data from a page and update the overall information held
        by the crawler
        """

        self.links_to_visit.add(page.get_links())
        self.images.add(page.get_images())

    def download_all_images(self):
        """Download all of the images on a page through the use of the image
        downloader
        """

        downloader = ImageDownloader(self.images)
        downloader.run()

    def visit_multiple_pages(self):
        """Visit multiple pages and collect the information from each of them
        """

        pages_visited = 0

        while pages_visited < self.settings.get_user_page_lim:
            self.visit_page(self.links_to_visit.pop())
            pages_visited += 1


class Page:
    """Store the information of a single page"""

    def __init__(self, url):
        self.url = url
        self.url_base = self.get_url_base()
        self.links = self.collect_links()
        self.images = self.collect_images()

    def get_url_base(self):
        """Return the base of the page's url."""

        # For example, in https://en.wikipedia.org/wiki/Computer_science
        # the base url is https: // en.wikipedia.org

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
        """Collect all of the images on the page and add them to a set as an
        ImageData object
        """

        page_request = urllib.request.Request(self.url)
        response = urllib.request.urlopen(page_request)
        soup = BeautifulSoup(response, "lxml")  # Specify the parser to use

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
        """Return the set of all links on the page"""

        return self.links

    def get_images(self):
        """Return the set of all images on the page"""

        return self.images


class ImageData:
    """Contain the information related to a single image"""

    def __init__(self, image_url, alt_text):
        self.image_url = image_url
        self.alt_text = alt_text
        self.file_name = self.make_name()
        print(self.__dict__)

    def make_name(self):
        """Create the name of the file based off of the alt text, or from a
        random number if none is provided"""

        photo_name = self.alt_text
        # Deal with missing alt text
        if len(photo_name) == 0:
            photo_name = "unnamed_img_" + str(random.randrange(10000))
        file_name = photo_name + ".jpeg"
        return file_name

    def get_image_url(self):
        """Return the absolute url that the image can be found at"""

        return self.image_url

    def get_alt_text(self):
        """Return the alt text of an image. Lack of an alt text returns a blank
        string
        """

        return self.alt_text

    def get_file_name(self):
        """Return the complete name for the image file"""

        return self.file_name


class ImageDownloader:
    """Download the images at the given url"""

    def __init__(self, img_objects):
        self.imgs = img_objects

    def clear_folder(self):
        """Empty the image folder of images from a previous run"""
        pass

    def download_images(self):
        """Download all of the images in the list of image objects"""

        for img in self.imgs:
            image_file = open("../images/" + img.get_file_name + ".jpeg", "wb")
            image_file.write(urllib.request.urlopen(img.get_image_url())
                             .read())
            image_file.close()

    def run(self):
        """Clear the folder out and download all of the images"""

        self.clear_folder()
        self.download_images()


class Program:
    """Hold the main program"""

    def __init__(self):
        self.user_input = UserInput()
        self.user_input.request_user_settings()

        self.crawler = Crawler(self.user_input)

    def run(self):
        pass

if __name__ == "__main__":
    crawler_collage = Program()
    crawler_collage.run()
