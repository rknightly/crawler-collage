#!/usr/bin/python3

import urllib.request
import urllib.parse
from urllib import request, error
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import os
from collage_maker import collage_maker
import hashlib


def verify_real_url(url):
    """Return True if a url is legitimate or false if it is not"""

    # Quick test to see if it starts with http
    return True if url[:4] == "http" else False


def find_checksum(file_path):
    """Return the checksum of the file at the given file path"""

    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        # Update the checksum with 4096 bytes at a time
        for chunk in iter(lambda: file.read(4096), b''):
            hash_md5.update(chunk)

    return hash_md5


class CrawlerUserInput:
    """Get the page to crawl from the user"""

    def __init__(self):
        self.user_url = ""
        self.user_page_lim = 0

    def find_user_url(self):
        """Get the url to start on from the user"""
        user_url = input("Start page -> ")
        while not verify_real_url(user_url):
            print("[Error] Invalid url given")
            user_url = input("Start page -> ")

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
        self.images = []     # The order of the images is irrelevant
        self.total_unnamed_images = 0
        self.pages_visited = 0

    def visit_next_page(self):
        """Visit the first link in the list of links to visit, remove it from
        the list, and call the functions necessary upon visitation"""

        print("Visiting new page")
        can_visit = True
        # Return False if no more links can be visited, true if they can
        if len(self.links_to_visit) > 0:
            url = self.links_to_visit.pop(0)
            # Only visit valid link
            if url[:4] == "http":
                page = Page(url)
                page.collect_images(
                    total_unnamed_image_count=self.total_unnamed_images)
                self.total_unnamed_images += page.get_unnamed_images_on_page()
                self.dump_data(page)
                if page.get_could_visit():
                    self.pages_visited += 1
        else:
            can_visit = False

        return can_visit

    def dump_data(self, page):
        """
        Take the data from a page and update the overall information held
        by the crawler
        """

        self.links_to_visit.extend(page.get_links())
        # Only add the image to the list if none of the others have the same
        # name
        for image in page.get_images():
            already_added = False
            for image_already_added in self.images:
                if image_already_added.get_file_name() == \
                        image.get_file_name():
                    already_added = True
            if not already_added:
                self.images.append(image)

    def download_all_images(self):
        """Download all of the images on a page through the use of the image
        downloader
        """

        downloader = ImageDownloader(self.images)
        downloader.run()

    def visit_multiple_pages(self):
        """Visit multiple pages and collect the information from each of them
        """

        while self.pages_visited < self.settings.get_user_page_lim():
            # Stop visiting pages if links to visit runs out
            if not self.visit_next_page():
                break

    def run(self):
        """Run the necessary functions for the crawler to finish its job"""

        self.visit_multiple_pages()
        self.download_all_images()


class Page:
    """Store the information of a single page"""

    def __init__(self, url):
        self.url = url
        self.unnamed_images_on_page = 0
        self.url_base = self.get_url_base()
        self.links = self.collect_links()
        self.could_visit = True

        # Hold images as blank list until the method is called so that the
        # number of unnamed images can be passed in
        self.images = []

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
        try:
            response = request.urlopen(page_request)

        except urllib.error.HTTPError:
            print("A page was unreachable")
            self.could_visit = False
            response = ""

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
        legit_links = filter(verify_real_url, abs_links)

        return legit_links

    def collect_images(self, total_unnamed_image_count):
        """Collect all of the images on the page and add them to a list as an
        ImageData object
        """
        current_unnamed_image_count = total_unnamed_image_count
        page_request = urllib.request.Request(self.url)
        try:
            response = urllib.request.urlopen(page_request)
        except urllib.error.HTTPError:
            self.could_visit = False
            print("Some images were unreachable")
            response = ""

        # Specify the parser to use
        soup = BeautifulSoup(response, "html.parser")

        images = []

        # Keep a count of the images with no designated file name

        for img in soup.findAll('img'):
            temp = img.get('src')

            image_url = self.verify_abs_url(test_url=temp)

            # If the link is not a normal link, forget it
            if image_url[:4] != "http":
                continue
            image_alt_text = str(img.get("alt"))
            image = ImageData(image_url=image_url, alt_text=image_alt_text,
                              unnamed_image_count=current_unnamed_image_count)
            if image.is_unnamed():
                current_unnamed_image_count += 1
                self.unnamed_images_on_page += 1
            images.append(image)

        self.images = images

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

    def get_unnamed_images_on_page(self):
        """Return the number of unnamed images on the page"""

        return self.unnamed_images_on_page

    def get_could_visit(self):
        """Return whether or not the page was able to be visited"""

        return self.could_visit


class ImageData:
    """Contain the information related to a single image"""

    def __init__(self, image_url, alt_text, unnamed_image_count):
        self.image_url = image_url
        self.alt_text = alt_text
        self.unnamed_image_count = unnamed_image_count
        self.file_name = self.make_name()

    def make_name(self):
        """Create the name of the file based off of the alt text, or from a
        random number if none is provided"""

        photo_name = self.get_alt_text()
        # Deal with missing alt text
        if self.is_unnamed():
            photo_name = "unnamed_img_" + str(self.unnamed_image_count)
        file_name = photo_name + ".png"

        return file_name

    def get_image_url(self):
        """Return the absolute url that the image can be found at"""

        return self.image_url

    def get_alt_text(self):
        """Return the alt text of an image with spaces replaced with
        underscores. Lack of an alt text returns a blank string
        """

        # Remove commas and periods
        alt_text = re.sub(r',|\.|/', '', self.alt_text)
        # Replaces spaces with underscores
        alt_text = re.sub(r'\s', '_', alt_text)
        # Ensure that the file name is not too long
        if len(alt_text) >= 30:
            alt_text = alt_text[:30]
        return alt_text

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
        self.image_checksums = set()

    def download_images(self):
        """Download all of the images in the list of image objects"""
        print("Pictures to download:", len([img.get_file_name() for img
                                            in self.imgs]))
        for img in self.imgs:
            print("Downloading image")
            image_path = os.path.join(self.image_folder.get_path(),
                                      img.get_file_name())
            prior_amount = len(os.listdir("./images"))

            # Don't download any images that would overwrite an existing one
            if os.path.exists(image_path):
                continue

            image_file = open(image_path, "wb")

            # Ignore any images that are unreachable for any reason
            try:
                image_request = urllib.request.urlopen(img.get_image_url())
            except urllib.error.HTTPError:
                print("Image unreachable")
                continue

            # Ignore blank images
            try:
                web_file_size = int(image_request.info()["Content-Length"])
            except TypeError:
                # The length of the photo is not provided. Take no risks
                continue
            # ID blank images by having unreasonably small file size
            if web_file_size <= 100:
                continue

            image_file.write(image_request.read())
            image_file.close()

            image_checksum = find_checksum(image_path)
            # Delete the file if an identical image was downloaded earlier
            if image_checksum in self.image_checksums:
                os.remove(image_path)
            self.image_checksums.add(image_checksum)

            later_amount = len(os.listdir("./images"))
            if not later_amount > prior_amount:
                print("[WARNING] Image not downloaded------------------------")
        print("Images downloaded")

    def run(self):
        """Clear the folder out and download all of the images"""

        self.download_images()


class CollageMaker:
    def __init__(self, user_input):
        self.user_input = user_input
        self.ensure_folder_exists()

    def run(self):
        collage_maker.run(self.user_input.get_settings())

    def ensure_folder_exists(self):
        collage_directory = Directory(path='./collages')
        self.user_input.set_output_dir(collage_directory.get_path())


class CollageUserInput:
    def __init__(self):
        self.folder = './images'
        self.output_dir = './collages'
        self.output_file_name = 'collage.png'
        self.find_output_name()

        self.output = self.set_output()

        self.width = 1000
        self.initial_height = 25
        self.shuffle = False

        self.settings = self.find_settings()

    def find_settings(self):
        settings = collage_maker.Settings(folder=self.folder,
                                          output=self.output,
                                          width=self.width,
                                          initial_height=self.initial_height,
                                          shuffle=self.shuffle)
        return settings

    def find_output_name(self):
        name = input("Name of collage without an extension -> ")
        name += ".png"
        self.output_file_name = name

    def set_output_dir(self, new_output_dir):
        self.output_dir = new_output_dir
        self.set_output()

    def set_output(self):
        """Return the full path to the output collage file when given the
        directory and name of the collage file"""

        collage_file_path = os.path.join(self.output_dir,
                                         self.output_file_name)
        self.output = collage_file_path
        return collage_file_path

    def get_settings(self):
        return self.settings


class Program:
    """Hold the main program"""

    def __init__(self):
        self.crawler_user_input = CrawlerUserInput()
        self.crawler_user_input.request_user_settings()

        self.crawler = Crawler(self.crawler_user_input)

    def run(self):
        self.crawler.run()

        collage_input = CollageUserInput()
        collage = CollageMaker(user_input=collage_input)
        collage.run()

if __name__ == "__main__":
    crawler_collage = Program()
    crawler_collage.run()
