from unittest import TestCase


class BasicSettings:
    """Contain a basic user input to use in test cases"""

    def __init__(self):
        from crawler_collage import UserInput

        self.settings = UserInput()
        self.settings.user_url = "http://rknightly.github.io/introHtml.html"
        self.settings.user_page_lim = 2

    def change_to_small_wiki(self):
        self.settings.user_url = "https://en.wikipedia.org/wiki/" \
                                 "Lumbar"


class TestVisitPage(TestCase, BasicSettings):
    """Ensure that a page can be visited and that the data is updated
    accordingly
    """

    def test_single_visit(self):
        from crawler_collage import UserInput, Crawler, ImageData

        BasicSettings.__init__(self)
        crawler = Crawler(user_settings=self.settings)
        crawler.visit_next_page()
        self.assertEqual(crawler.links_to_visit,
                         ["http://rknightly.github.io/one.html",
                          "http://rknightly.github.io/two.two.html",
                          "http://rknightly.github.io/three.html",
                          "https://www.youtube.com/watch?v=WSeNSzJ2-Jw",
                          "http://www.intro-webdesign.com/"],
                         "Links were incorrectly collected upon visitation of"
                         " a single page")
        expected_image = ImageData(image_url="http://www.intro-webdesign.com/"
                                             "images/newlogo.png",
                                   alt_text="WD4E")

        # Ensure that the attributes of the expected image are equal to the
        # attributes of the image popped from the set of images
        self.assertTrue(crawler.images.pop().__dict__ ==
                        expected_image.__dict__,
                        "Image was incorrectly collected from single page")


class TestDumpData(TestCase, BasicSettings):
    """Ensure that the dump_data method appropriately updates the attributes
    of the crawler
    """

    def test_single_dump(self):
        from crawler_collage import Crawler, Page, ImageData

        BasicSettings.__init__(self)
        crawler = Crawler(user_settings=self.settings)
        test_page = Page("http://rknightly.github.io/introHtml.html")
        crawler.dump_data(test_page)

        self.assertEqual(crawler.links_to_visit,
                         # Link of page should still be present because the
                         # dump was performed in isolation, without a different
                         # action that would have removed any links
                         ["http://rknightly.github.io/introHtml.html",
                          "http://rknightly.github.io/one.html",
                          "http://rknightly.github.io/two.two.html",
                          "http://rknightly.github.io/three.html",
                          "https://www.youtube.com/watch?v=WSeNSzJ2-Jw",
                          "http://www.intro-webdesign.com/"],
                         "Links were incorrectly dumped")

        expected_image = ImageData(image_url="http://www.intro-webdesign.com/"
                                             "images/newlogo.png",
                                   alt_text="WD4E")

        # Ensure that the attributes of the expected image are equal to the
        # attributes of the image popped from the set of images
        self.assertTrue(crawler.images.pop().__dict__ ==
                        expected_image.__dict__,
                        "Image was incorrectly dumped")


class TestDownloadAllImages(TestCase, BasicSettings):
    """Ensure that all images are downloaded when the download all images
    method is called"""

    @staticmethod
    def check_how_many_pics():
        import os.path

        # Check how many files are in images folder
        num_of_files = (len([name for name in os.listdir('./images') if
                        os.path.isfile(os.path.join('./images', name))]))

        return num_of_files

    def test_no_images(self):
        from crawler_collage import Crawler

        BasicSettings.__init__(self)

        crawler = Crawler(self.settings)
        crawler.download_all_images()

        self.assertEqual(self.check_how_many_pics(), 0,
                         "Images incorrectly downloaded when no images were "
                         "collected")

    def test_multiple_images(self):
        from crawler_collage import Crawler

        BasicSettings.__init__(self)

        self.change_to_small_wiki()

        crawler = Crawler(self.settings)
        crawler.visit_next_page()
        crawler.download_all_images()
        self.assertEqual(self.check_how_many_pics(), 5,
                         "Images incorrectly downloaded when several images "
                         "were collected")

    def test_multiple_pages(self):
        pass

class TestVisitMultiplePages(TestCase):
    pass