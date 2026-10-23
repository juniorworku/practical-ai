import unittest
from core import process

class EvidenceTests(unittest.TestCase):
    def doc(self, text):
        return {'id':'one:policy','revision':'r1','text':text}

    def test_exception_beyond_old_cut_is_preserved(self):
        text = 'Refunds within 14 days. ' + 'Policy detail. ' * 23 + 'Opened items are excluded.'
        self.assertGreater(len(text), 350)
        result = process('refunds', 'fixture', [self.doc(text)])
        self.assertEqual(result['status'], 'needs_review')
        self.assertIn('Opened items are excluded.', result['text'])
        self.assertEqual(result['context_chars'], len(text))

    def test_relevant_oversize_is_not_silently_truncated(self):
        result = process('refunds', 'fixture', [self.doc('Refunds ' + 'x'*700)])
        self.assertEqual(result['status'], 'needs_correction')
        self.assertIsNone(result['text'])
        self.assertFalse(result['citations'])

    def test_source_revision_changes_candidate_key(self):
        doc = self.doc('Refunds within 14 days.')
        before = process('refunds', 'fixture', [doc])
        after = process('refunds', 'fixture', [{**doc, 'revision':'r2'}])
        self.assertNotEqual(before['cache_key'], after['cache_key'])
        self.assertFalse(before['cache_hit'])

    def test_no_evidence_and_forbidden_action(self):
        self.assertEqual(process('wallpaper', 'fixture', [])['status'], 'abstain')
        self.assertEqual(process('delete refunds', 'fixture', [])['status'], 'denied')

if __name__ == '__main__':unittest.main()
