from unittest import TestCase


class TestMakeName(TestCase):

    def test_alt_given(self):
        from crawler_collage import ImageData
        image = ImageData(image_url="https://en.wikipedia.org/static/images/"
                                    "wikimedia-button.png",
                          alt_text="Wikimedia Foundation",
                          unnamed_image_count=5)
        self.assertEqual(image.get_file_name(), "Wikimedia_Foundation.jpeg",
                         "File name was not correctly found when given an ")

    def test_no_alt(self):
        from crawler_collage import ImageData
        image = ImageData(image_url="https://en.wikipedia.org/static/images/"
                                    "wikimedia-button.png",
                          alt_text="",
                          unnamed_image_count=6)
        self.assertEqual(image.get_file_name(), "unnamed_img_6.jpeg",
                         "File name was not correctly found when no alt text"
                         " was given ")

    def test_multiple_underscores(self):
        from crawler_collage import ImageData
        image = ImageData(image_url="https://en.wikipedia.org/static/images/"
                                    "wikimedia-button.png",
                          alt_text="fun picture of beach",
                          unnamed_image_count=6)
        self.assertEqual(image.get_file_name(), "fun_picture_of_beach.jpeg",
                         "Underscores were not properly inserted into the"
                         " name with several spaces")

    def test_extra_characters(self):
        from crawler_collage import ImageData
        image = ImageData(image_url="https://en.wikipedia.org/static/images/"
                                    "wikimedia-button.png",
                          alt_text="fighter jet/ no. 1, best in Texas",
                          unnamed_image_count=6)
        self.assertEqual(image.get_file_name(),
                         "fighter_jet_no_1_best_in_Texas.jpeg",
                         "Underscores were not properly inserted into the"
                         " name with several spaces")
