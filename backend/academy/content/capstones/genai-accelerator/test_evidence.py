import unittest
from evidence import select_document

class ContextTests(unittest.TestCase):
    def test_unmatched_exception_is_retained(self):
        chunks=[{'position':0,'text':'Refunds within 14 days'},
                {'position':1,'text':'Unused items only'}]
        selected,used=select_document(chunks,'refunds')
        self.assertEqual(selected,chunks)
        self.assertEqual(used,sum(len(c['text']) for c in chunks))

    def test_oversize_is_not_a_partial_success(self):
        with self.assertRaisesRegex(ValueError,'context_review_required'):
            select_document([{'position':0,'text':'Refunds'},
                             {'position':1,'text':'x'*1000}],'refunds')

    def test_unknown_topic_still_abstains(self):
        self.assertEqual(select_document([{'position':0,'text':'Refunds'}],'wallpaper'),([],0))

if __name__=='__main__':unittest.main()
