import importlib, os, unittest
lab=importlib.import_module(os.getenv('LAB_MODULE','exercises'))
class Retrieval(unittest.TestCase):
    def test_relevance_order_and_identity(self):
        passages=[{'id':'z','text':'return item policy'},{'id':'a','text':'return item policy'},{'id':'b','text':'shipping'}]
        self.assertEqual([p['id'] for p in lab.retrieve('RETURN item',passages,2)],['a','z'])
        self.assertEqual(passages[0]['text'],'return item policy')
    def test_no_evidence(self):self.assertEqual(lab.retrieve('warranty',[{'id':'a','text':'shipping'}]),[])
    def test_invalid_limit(self):
        with self.assertRaises(ValueError):lab.retrieve('x',[],0)
class Extraction(unittest.TestCase):
    def test_exact_decimal(self):
        self.assertEqual(lab.validate_record({'quantity':3,'unit_price':'0.10','total':'0.30','currency':'TEST'}),[])
    def test_mismatch_and_unknown(self):
        errors=lab.validate_record({'quantity':12,'unit_price':'25','total':'250'})
        self.assertIn('total:mismatch',errors);self.assertIn('currency:missing',errors)
    def test_bad_types_and_nonfinite(self):
        errors=lab.validate_record({'quantity':True,'unit_price':'NaN','total':'bad','currency':'TEST'})
        self.assertEqual(set(errors),{'quantity:invalid','unit_price:invalid','total:invalid'})
    def test_no_fractional_quantity(self):
        self.assertIn('quantity:invalid',lab.validate_record({'quantity':'1.5','unit_price':'2','total':'3','currency':'TEST'}))
class Citations(unittest.TestCase):
    def test_reference_integrity(self):
        self.assertTrue(lab.validate_citations('draft',['p1'],['p1','p2']))
        for answer,refs in [('draft',[]),('draft',['unknown']),('draft',['p1','p1']),('', ['p1']),('draft',[{'id':'p1'}])]:
            self.assertFalse(lab.validate_citations(answer,refs,['p1']))
class Agent(unittest.TestCase):
    def test_stop_on_answer(self):
        self.assertEqual(lab.run_agent(lambda trace:'retrieve' if not trace else 'answer'),{'status':'answer','trace':['retrieve','answer']})
    def test_repetition_limit(self):self.assertEqual(lab.run_agent(lambda trace:'retrieve',2)['status'],'step_limit')
    def test_unknown_action(self):self.assertEqual(lab.run_agent(lambda trace:'send_email')['status'],'failed')
    def test_exception(self):
        def fail(trace):raise TimeoutError('fixture')
        self.assertEqual(lab.run_agent(fail)['status'],'failed')
class Routing(unittest.TestCase):
    def test_confusion_keeps_failures(self):
        result=lab.routing_metrics(['account','shipping','account'],['shipping','shipping','account'])
        self.assertEqual(result['count'],3);self.assertEqual(result['correct'],2)
        self.assertEqual(result['confusion']['account'],{'shipping':1,'account':1})
    def test_length_mismatch(self):
        with self.assertRaises(ValueError):lab.routing_metrics(['account'],[])
class Economics(unittest.TestCase):
    def test_review_and_exception_work(self):self.assertAlmostEqual(lab.net_minutes(40,20,4,10,.1,15),180)
    def test_negative_benefit_visible(self):self.assertEqual(lab.net_minutes(10,5,4,3,0,0),-20)
    def test_invalid_assumption(self):
        with self.assertRaises(ValueError):lab.net_minutes(10,5,4,3,2,0)
        with self.assertRaises(ValueError):lab.net_minutes(10,5,4,3,float('nan'),0)
if __name__=='__main__':unittest.main()
