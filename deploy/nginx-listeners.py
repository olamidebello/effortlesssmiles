#!/usr/bin/env python3
"""Discover existing address-specific HTTP listener groups without adding defaults."""
import ipaddress,json,re,subprocess,sys

def discover(config):
 result={'80':[], '443':[]}
 clean=re.sub(r'#[^\n]*','',config)
 for token in re.findall(r'\blisten\s+([^\s;]+)',clean):
  match=re.fullmatch(r'(\[[^]]+\]|[^:]+):(80|443)',token)
  if not match:continue
  host,port=match.groups()
  try:address=ipaddress.ip_address(host.strip('[]'))
  except ValueError:continue
  if address.is_unspecified:continue
  endpoint=('['+str(address)+']') if address.version==6 else str(address)
  if endpoint not in result[port]:result[port].append(endpoint)
 return result
if __name__=='__main__':
 run=subprocess.run(['nginx','-T'],capture_output=True,text=True)
 if run.returncode:sys.exit(run.stderr)
 print(json.dumps(discover(run.stdout)))
