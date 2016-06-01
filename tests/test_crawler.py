from unittest import TestCase


class TestCollectLinks(TestCase):

    def test_page(self):
        from crawler_collage import Crawler
        crawler = Crawler()
        links = crawler.collect_links("http://rknightly.github.io/introHtml"
                                      ".html")
        self.assertEqual(links,
                         {"https://www.youtube.com/watch?v=WSeNSzJ2-Jw",
                          "http://www.intro-webdesign.com/"},
                         "Links were not correctly collected from example"
                         " page")

class TestCollectImages(TestCase):

    def test_page(self):
        from crawler_collage import Crawler
        crawler = Crawler()
        crawler.collect_images("https://en.wikipedia.org/wiki/Micrometre")

class TestVerifyAbsUrl(TestCase):

    def test_abs_url(self):
        from crawler_collage import Crawler
        crawler = Crawler()
        self.assertEqual(crawler.verify_abs_url(
            page_url="https://en.wikipedia.org/wiki/Micrometre",
            img_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/40"
                    "/Youtube_icon.svg/256px-Youtube_icon.svg.png"),
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Youtube"
            "_icon.svg/256px-Youtube_icon.svg.png",
            "Absolute url incorrectly calculated when given absolute url")

    def test_rel_url(self):
        pass

    def incomplete_abs_url(self):
        pass