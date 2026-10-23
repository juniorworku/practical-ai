import unittest
from core import process
TEXT='Supplier: Studio\nQuantity: 2\nUnit price: 10.00\nCurrency: USD'

class ExtractionTests(unittest.TestCase):
    def test_raw_span_and_normalized_total_are_both_retained(self):
        result=process(TEXT,'fixture',[])
        self.assertEqual(result['record']['total'],'20.00')
        self.assertEqual(result['field_evidence']['unit price'],
                         [{'line':3,'raw':'Unit price: 10.00','value':'10.00'}])

    def test_duplicate_retains_both_conflicting_spans(self):
        result=process(TEXT+'\nQuantity: 9','fixture',[])
        self.assertEqual(result['status'],'needs_correction')
        self.assertIn('duplicate_quantity',result['issues'])
        self.assertEqual([s['line'] for s in result['field_evidence']['quantity']],[2,5])
        self.assertIsNone(result['text'])

    def test_missing_and_invalid_fields_do_not_become_defaults(self):
        for text in [TEXT.replace('Quantity: 2\n',''), TEXT.replace('10.00','NaN'),
                     TEXT.replace('Quantity: 2','Quantity: -2'),TEXT+'\nOwner: two']:
            with self.subTest(text=text):
                self.assertEqual(process(text,'fixture',[])['status'],'needs_correction')

if __name__=='__main__':unittest.main()
