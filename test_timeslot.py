import unittest
import sys
#sys.path.append('../')

from qualtrics_util import QualtricsDist

qd = QualtricsDist()
qd.initialize(config_file='config_test.yaml')


class TimeSlotMethods(unittest.TestCase):

    def call_check_time_slots(self,slots):
        result = qd.check_time_slots(slots)
        return result
    
    def test_check_numbers(self):
        slots = [800,1200,1600,2000]
        result = self.call_check_time_slots(slots)
        self.assertTrue(result)

    def test_check_numbers_bad(self):
        slots = [800,1200,1600,'a2000']
        result = self.call_check_time_slots(slots)
        self.assertFalse(result)

    def test_check_range_good(self):
        slots = [800,1200,1600,[2000,2100]]
        result = self.call_check_time_slots(slots)
        self.assertTrue(result)

    def test_check_range_bad(self):
        slots = [800,1200,1600,[2000-2100]]
        result = self.call_check_time_slots(slots)
        self.assertFalse(result)

    def test_check_range_bad2(self):
        slots = [800,1200,1600,[2100]]
        result = self.call_check_time_slots(slots)
        self.assertFalse(result)
        
    def test_check_range2(self):
        slots = [[800,900],[1200,1300],[1600,1700],[2000,2100]]
        result = self.call_check_time_slots(slots)
        self.assertTrue(result)
           
    def test_get_time1(self):
        slot = 800
        result = qd.get_time(slot)
        self.assertEqual(result, 800)

    def test_get_time_range(self):
        slot = [800,900]
        result = qd.get_time(slot)
        
        self.assertTrue((800 <= result <=900 ))
                           
if __name__ == '__main__':
    unittest.main()
    