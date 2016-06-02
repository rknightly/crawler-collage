from unittest import TestCase


class TestMakeName(TestCase):

    def test_alt_given(self):
        from crawler_collage import ImageData
        image = ImageData(image_url="https://en.wikipedia.org/static/images/"
                                    "wikimedia-button.png",
                          alt_text="Wikimedia Foundation")
        self.assertEqual(image.get_file_name(), "Wikimedia Foundation.jpeg",
                         "File name was not correctly found when given an ")

    def test_no_alt(self):
        from crawler_collage import ImageData
        image = ImageData(image_url="https://en.wikipedia.org/static/images/"
                                    "wikimedia-button.png",
                          alt_text="")
        self.assertEqual(image.get_file_name()[:12], "unnamed_img_",
                         "File name was not correctly found when no alt text"
                         "was given ")