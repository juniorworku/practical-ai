"""Purchase-request extraction: explicitly deterministic parsing, not AI extraction."""
from decimal import Decimal
import re
KIND='workshops'
VERSION='purchase-schema-v2'
def process(text,mode,documents):
 if mode=='timeout':raise TimeoutError('fixture')
 if mode=='malformed':raise ValueError('fixture_invalid_output')
 fields={};issues=[];evidence={}
 for number,line in enumerate(text.splitlines(),1):
  if not line.strip():continue
  if ':' not in line:issues.append('unrecognized_line');continue
  key,value=line.split(':',1);key=key.strip().lower()
  evidence.setdefault(key,[]).append({'line':number,'raw':line,'value':value.strip()})
  if key in fields:
   issues.append('duplicate_'+key)
   continue  # Retain both spans, but never silently overwrite the first value.
  fields[key]=value.strip()
 required={'supplier','quantity','unit price','currency'}
 if set(fields)!=required:issues.append('missing_or_extra_fields')
 if not fields.get('supplier'):issues.append('supplier_required')
 quantity=fields.get('quantity','')
 if not quantity.isascii() or not quantity.isdigit() or not 1<=int(quantity)<=1000:issues.append('quantity_integer_1_to_1000')
 price=fields.get('unit price','')
 if not re.fullmatch(r'\d{1,6}\.\d{2}',price):issues.append('unit_price_two_decimals')
 if fields.get('currency')!='USD':issues.append('currency_not_supported')
 if issues:return {'status':'needs_correction','text':None,'citations':[],'issues':issues,'field_evidence':evidence,'trace':['parse','validate','manual_correction']}
 total=Decimal(price)*int(quantity)
 # A source excerpt, never an invented missing field or a silent zero.
 result={'supplier':fields['supplier'],'quantity':int(quantity),'unit_price':price,'currency':'USD','total':str(total)}
 return {'status':'needs_review','text':str(result),'record':result,'field_evidence':evidence,'citations':['submitted-request'],'context_chars':len(text),'trace':['parse','validate','calculate','await_confirmation']}
