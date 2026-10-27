#!/usr/bin/env python3
"""Detach only this domain from foreign Nginx server_name directives."""
import argparse,hashlib,json,pathlib,re,subprocess,sys

def detach(text,domain):
 def change(match):
  names=match.group(2).split()
  if domain not in names:return match.group(0)
  names=[name for name in names if name!=domain]
  return match.group(1)+' '.join(names or ['effortlesssmiles-detached.invalid'])+';'
 # Match uncommented directives, including multiline server_name lists.
 return re.sub(r'(?m)(^[ \t]*server_name\s+)((?:(?!#)[^;])+);',change,text)

def main():
 p=argparse.ArgumentParser();p.add_argument('--domain',required=True);p.add_argument('--managed-vhost',required=True);p.add_argument('--backup',required=True);a=p.parse_args()
 if not re.fullmatch(r'[a-z0-9.-]+',a.domain):sys.exit('Invalid domain')
 result=subprocess.run(['nginx','-T'],capture_output=True,text=True)
 if result.returncode:sys.exit('Existing Nginx configuration invalid: '+result.stderr)
 managed=pathlib.Path(a.managed_vhost).resolve();files=[]
 for name in re.findall(r'^# configuration file (.*):$',result.stdout,re.M):
  path=pathlib.Path(name).resolve()
  if path!=managed and path not in files:files.append(path)
 originals={};backup=pathlib.Path(a.backup)/'routing';changed=[]
 try:
  for path in files:
   old=path.read_text();new=detach(old,a.domain)
   if new==old:continue
   backup.mkdir(parents=True,exist_ok=True,mode=0o700)
   target=backup/(hashlib.sha256(str(path).encode()).hexdigest()+'.conf')
   target.write_text(old);target.chmod(0o600)
   originals[path]=old;path.write_text(new);changed.append({'path':str(path),'backup':str(target)})
  check=subprocess.run(['nginx','-t'],capture_output=True,text=True)
  if check.returncode:raise RuntimeError(check.stderr)
  if changed:(backup/'manifest.json').write_text(json.dumps(changed,indent=2))
 except Exception:
  for path,old in originals.items():path.write_text(old)
  raise
 print(json.dumps({'changed':bool(changed),'files':changed,'domain':a.domain}))
if __name__=='__main__':main()
