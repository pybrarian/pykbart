import unittest

import kbart

# run 'python -m test.kbarttest' for test cases to properly run 
class KbartTest(unittest.TestCase):

    def test_rp(self):
        
        new_kbart_1 = kbart.Kbart(rp=1)
        new_kbart_default = kbart.Kbart()

        self.assertEqual(new_kbart_1.kbart_fields[0], 'publication_title')
        self.assertEqual(new_kbart_default.kbart_fields[15], 'notes')
        self.assertRaises(kbart.exceptions.NotValidRP,
                          kbart.Kbart,
                          rp=3)


    def test_provider(self):
        self.assertRaises(kbart.exceptions.ProviderNotFound,
                          kbart.Kbart,
                          provider='myself')

if __name__ == '__main__':
    unittest.main()
