import unittest
import datetime

from fitjstats.views import build_url, RE_RX, RE_SCALE, RE_GENDER
from fitjstats.views import get_datetime, get_new_data
from fitjstats import settings

class TestCrawler(unittest.TestCase):

    def test_build_url(self):
        self.assertEqual(
            build_url(datetime.date(2018, 10, 10)),
            "https://crossfit.com/" \
            + "comments/api/v1/topics/" \
            + "mainsite.20181010/comments"
        )
        self.assertEqual(
            build_url(datetime.date(2018, 1, 1)),
            "https://crossfit.com/" \
            + "comments/api/v1/topics/" \
            + "mainsite.20180101/comments"
        )

    def test_static_dir(self):
        self.assertTrue("/home/kevin/fitjstats/fitjstats/static" in 
            settings.STATICFILES_DIRS)

    def test_rx_exists_at_start_of_str(self):
        cmt = "rx\'d: 25:35 had to use a treadmill for the run"
        self.assertTrue(RE_RX.search(cmt).group(1) == 'rx')

    def test_rx_exists_in_mid_of_str(self):
        cmt = ('m/32/6\\\'2"/218lbs\\n27:21 rx\\\'d \
            \ngot to work on double unders\\n')
        self.assertTrue(RE_RX.search(cmt).group(1) == 'rx')

        cmt = "as rx\'d\\n25# med ball\\n\\n23:32(pr)"
        self.assertTrue(RE_RX.search(cmt).group(1) == 'rx')
        
        cmt = ('m/28/5\'7"/175\n\naround 23 min. as \
            rx\'d (didn\'t have a stopwatch\n\n')
        self.assertTrue(RE_RX.search(cmt).group(1) == 'rx')

    def test_rx_exists_at_end_of_str(self):
        cmt = "135 rx"
        self.assertTrue(RE_RX.search(cmt).group(1) == 'rx')

    def test_rx_not_in_str(self):
        cmts = ['made up string rxa',
                'made up string rxb',
                'made up string rxad',
                'rxa loreum ipsum',
                'rxf loreum ipsum',
                'arx loreum ipsum',
                'r\nx',
            ]
        for cmt in cmts:
            self.assertTrue(RE_RX.search(cmt) is None)

    def test_scale_exists_at_start_of_str(self):
        cmt = "Scaled it 19:20"
        self.assertTrue(RE_SCALE.search(cmt).group(1) == 'Scale')
        
    def test_scale_exists_in_mid_of_str(self):
        cmt = "I scaled it 19:20"
        self.assertTrue(RE_SCALE.search(cmt).group(1) == 'scale')

    def test_scale_exists_at_end_of_str(self):
        cmt = "19:20 scaled."
        self.assertTrue(RE_SCALE.search(cmt).group(1) == 'scale')

    def test_scale_not_in_str(self):
        cmts = ['made up string scaleb',
                'made up string scales',
                'scales well with',
                'rescale sum',
            ]
        for cmt in cmts:
            self.assertTrue(RE_SCALE.search(cmt) is None)
        

    def test_gender_exists_at_start_of_str(self):
        cmt = "m38/5'8/165\n\nas rx'd 35:02"
        self.assertTrue(RE_GENDER.search(cmt).group(1) == 'm')
        
        cmt = ('F/41/5\'6"/145\n\nHalf-Nutts (~50% in some \
            aspect of each movement):\n\n10 band-assist HSPU \
            to 2-3" board stack\n125# DL, 15 reps\n25 box jumps, \
            18"\n25 pull-ups\n50 wall balls, 14#\n100 DU\'s \n\
            400m with 25# plate\n\n21:02').lower()
        self.assertTrue(RE_GENDER.search(cmt).group(1) == 'f')
        
        cmt = ("F 30/5'6/200\n\n31:30\nHSPU w/ toes on bench\n\
            150 dL\nAssisted pullups\n500 single jr\n\nWorking \
            on doing everything as prescribed").lower()
        self.assertTrue(RE_GENDER.search(cmt).group(1) == 'f')

    def test_gender_exists_in_mid_of_str(self):
        cmt = '51/m/190\n\nSubbed 24"box. 31:17'
        self.assertTrue(RE_GENDER.search(cmt).group(1) == 'm')

        cmt = "24:37 rx m/40/5’8”/160"
        self.assertTrue(RE_GENDER.search(cmt).group(1) == 'm')

    def test_gender_not_in_str(self): 
        cmt = ('DU\'s \n 400m with 25# plate\n\n21:02').lower()
        self.assertTrue(RE_GENDER.search(cmt) is None)

        cmt = '95, 105, 115, 125, 130, 135 (f), 115, 120'
        self.assertTrue(RE_GENDER.search(cmt) is None)

        cmt = '60F-60-60-60-61-63-65-66F-66F-66F (Kg)'
        self.assertTrue(RE_GENDER.search(cmt) is None)

        cmt = "correct me if i’m wrong."
        self.assertTrue(RE_GENDER.search(cmt) is None)

    def test_rx_not_at_end_of_str(self):
        not_rx = "did 200 single unders instead, rest as rx'd-35:20"
        pass

    def test_get_datetime(self):
        dt = "2018-11-04T10:18:29+0000"
        self.assertTrue([2018, 11, 4, 10, 18, 29] == get_datetime(dt))

    def test_get_context(self):
        import pytz
        context = get_new_data(datetime.date(2018,1,1))
        detail = context['details'][1]
        self.assertTrue(
            detail.comment_text == "Well that was an interesting article and not at all surprising. For big corp it's really the only logical step to keep the big money ball rolling and doing what worked in first world countries for so long. Sad that the world is so corrupt."
        )
        self.assertTrue(
            #"2018-01-01T02:42:58+0000"
            detail.created == datetime.datetime(2018,1,1,2,42,58, tzinfo=pytz.UTC)
        )
        self.assertTrue(
            detail.commenter.first_name == "Nathan"
        )
        self.assertTrue(
            detail.commenter.last_name == "Jones"
        )
        self.assertTrue(
            detail.commenter.picture_url == 
            "https://profilepicsbucket.crossfit.com/fbe15-P241707_7-184.jpg"
        )
        self.assertTrue(
            #"2016-03-30T18:23:58+0000"
            detail.commenter.created == datetime.datetime(2016,3,30,18,23,58, tzinfo=pytz.UTC)
        )

if __name__ == "__main__":
    unittest.main()
