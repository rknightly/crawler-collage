#!/usr/bin/python3

import urllib.request
import urllib.parse
from urllib import request
from urllib.parse import urlparse, urljoin
from urllib import error
from bs4 import BeautifulSoup
import random
import os


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
        self.links_to_visit = [self.settings.get_user_url()]
        self.images = set()     # The order of the images is irrelevant

    def visit_next_page(self):
        """Visit the first link in the list of links to visit, remove it from
        the list, and call the functions necessary upon visitation"""

        print("Visiting new page")
        can_visit = True
        # Return False if no more links can be visited, true if they can
        if len(self.links_to_visit) > 0:
            url = self.links_to_visit.pop(0)
            print(url)
            page = Page(url)
            self.dump_data(page)
        else:
            can_visit = False

        return can_visit

    def dump_data(self, page):
        """
        Take the data from a page and update the overall information held
        by the crawler
        """

        self.links_to_visit.extend(page.get_links())
        self.images.update(page.get_images())

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

        while pages_visited < self.settings.get_user_page_lim():
            if self.visit_next_page():
                pages_visited += 1
            else:
                break

    def run(self):
        """Run the necessary functions for the crawler to finish its job"""

        self.visit_multiple_pages()
        self.download_all_images()


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

        # Specify the parser to use
        soup = BeautifulSoup(response, "html.parser")

        # Grab all of the links with BeautifulSoup and only keep the ones with
        # "www." to ensure that self-referencing links are not collected
        # links = {link['href'] for link in soup.findAll('a')}

        links = []
        for link in soup.findAll('a'):
            try:
                links.append(link['href'])
            except KeyError:
                pass

        abs_links = [self.verify_abs_url(test_url=link) for link in links]

        return abs_links

    def collect_images(self):
        """Collect all of the images on the page and add them to a set as an
        ImageData object
        """

        page_request = urllib.request.Request(self.url)
        response = urllib.request.urlopen(page_request)

        # Specify the parser to use
        soup = BeautifulSoup(response, "html.parser")

        images = set()

        # Keep a count of the images with no designated file name
        # unnamed_image_count = 0

        for img in soup.findAll('img'):
            temp = img.get('src')

            image_url = self.verify_abs_url(test_url=temp)
            image_alt_text = str(img.get("alt"))
            image = ImageData(image_url=image_url, alt_text=image_alt_text)
            # if image.is_unnamed():
            #     unnamed_image_count += 1
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

    def make_name(self):
        """Create the name of the file based off of the alt text, or from a
        random number if none is provided"""

        photo_name = self.alt_text
        # Deal with missing alt text
        if self.is_unnamed():
            photo_name = "unnamed_temp"
        file_name = photo_name + ".jpeg"

        return file_name

    def make_unnamed_title(self, unnamed_image_count):
        self.file_name = "unnamed_img_" + str(unnamed_image_count)

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

    def is_unnamed(self):
        unnamed = False
        if len(self.alt_text) <= 1:
            unnamed = True
        return unnamed


class Directory:
    """Contain the information and methods related to a folder"""

    def __init__(self, path):
        self.path = path    # Path should be given as a string
        self.ensure_dir_exists()

    def ensure_dir_exists(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def clear_dir(self):
        """Empty the directory"""

        print("Clearing directory")
        file_names = [name for name in os.listdir(self.path) if
                      os.path.isfile(os.path.join(self.path, name))]

        file_paths = [os.path.join(self.path, file_name) for file_name in
                      file_names]

        for file_path in file_paths:
            if os.path.isfile(file_path):
                os.remove(path=file_path)

    def get_path(self):
        return self.path


class ImageDownloader:
    """Download the images at the given url"""

    def __init__(self, img_objects):
        self.imgs = img_objects
        self.image_folder = Directory('./images')
        self.image_folder.clear_dir()

    def download_images(self):
        """Download all of the images in the list of image objects"""
        print("images:", [img.get_file_name() for img in self.imgs])
        print("Pictures to download:", len([img.get_file_name() for img
                                            in self.imgs]))
        unnamed_image_count = 0
        for img in self.imgs:
            if img.is_unnamed():
                img.make_unnamed_title(unnamed_image_count=
                                       unnamed_image_count)
                unnamed_image_count += 1
            print("Writing file")
            prior_amount = len(os.listdir("./images"))  # Test code -----------
            if os.path.exists(os.path.join("./images", img.get_file_name())):
                print("[WARNING] Image will be overwritten-------------------")
                print("Image name:", img.get_file_name())
            image_file = open(os.path.join(self.image_folder.get_path(),
                                           img.get_file_name()),
                              "wb")
            try:
                image_file.write(urllib.request.urlopen(img.get_image_url())
                             .read())
                image_file.close()

            except urllib.error.HTTPError:
                print("Image unable to write.")
                print("Url:", img.get_image_url())

            later_amount = len(os.listdir("./images"))  # Test code -----------
            if not later_amount > prior_amount:
                print("[WARNING] Image not downloaded------------------------")

    def run(self):
        """Clear the folder out and download all of the images"""

        self.download_images()


class Program:
    """Hold the main program"""

    def __init__(self):
        self.user_input = UserInput()
        self.user_input.request_user_settings()

        self.crawler = Crawler(self.user_input)

    def run(self):
        self.crawler.run()

if __name__ == "__main__":
    crawler_collage = Program()
    crawler_collage.run()
