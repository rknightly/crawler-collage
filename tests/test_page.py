from unittest import TestCase


class TestGetUrlBase(TestCase):

    def test_base_url(self):
        from crawler_collage import Page

        page = Page("https://en.wikipedia.org")
        self.assertEqual(page.get_url_base(), "https://en.wikipedia.org",
                         "Url base was incorrectly found when given the"
                         " url base to begin with")

    def test_page_url(self):
        from crawler_collage import Page

        page = Page("https://en.wikipedia.org/wiki/Micrometre")
        self.assertEqual(page.get_url_base(), "https://en.wikipedia.org",
                         "Url base was incorrectly found when given the"
                         " address of a specific webpage")


class TestCollectLinks(TestCase):

    def test_multiple_links(self):
        from crawler_collage import Page

        page = Page("http://rknightly.github.io/introHtml.html")
        print(page.get_links())
        self.assertEqual(page.get_links(),
                         {"https://www.youtube.com/watch?v=WSeNSzJ2-Jw",
                          "http://www.intro-webdesign.com/",
                          "http://rknightly.github.io/one.html",
                          "http://rknightly.github.io/two.two.html",
                          "http://rknightly.github.io/three.html"},
                         "Links were not correctly collected from example"
                         " page")


class TestCollectImages(TestCase):

    def test_single_img(self):
        from crawler_collage import Page, ImageData

        page = Page("http://rknightly.github.io/introHtml.html")
        expected_result = ImageData(image_url="http://www.intro-webdesign.com"
                                              "/images/newlogo.png",
                                    alt_text="WD4E")
        self.assertEqual(page.get_images().pop(), expected_result,
                         "Single image collected incorrectly")

    def test_multiple_imgs(self):
        from crawler_collage import Page

        page = Page("http://rknightly.github.io/index.html")
        self.assertEqual(len(page.get_images()), 13,
                         "Multiple images collected incorrectly")


class TestVerifyAbsUrl(TestCase):

    def test_abs_url(self):
        from crawler_collage import Page

        page = Page("https://en.wikipedia.org/wiki/Micrometre")
        self.assertEqual(page.verify_abs_url(
            test_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4"
                     "/40/Youtube_icon.svg/256px-Youtube_icon.svg.png"),
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Youtube"
            "_icon.svg/256px-Youtube_icon.svg.png",
            "Absolute url incorrectly calculated when given absolute url")

    def test_rel_url(self):
        from crawler_collage import Page

        page = Page("https://en.wikipedia.org/wiki/Micrometre")
        self.assertEqual(page.verify_abs_url(
            test_url="/wikipedia/commons/thumb/4/40/Youtube_icon.svg/256px-"
                     "Youtube_icon.svg.png"),
            "https://en.wikipedia.org/wikipedia/commons/thumb/4/40/Youtube_"
            "icon.svg/256px-Youtube_icon.svg.png",
            "Absolute url incorrectly calculated when given absolute url")

    def test_incomplete_abs_url(self):
        from crawler_collage import Page

        page = Page("https://en.wikipedia.org/wiki/Micrometre")
        self.assertEqual(page.verify_abs_url(
            test_url="//wikimedia.org"),
            "https://wikimedia.org",
            "Absolute url incorrectly calculated when given incomplete"
            " absolute url")
