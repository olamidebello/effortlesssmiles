#!/usr/bin/env python3
"""Read-only Nginx/port checks. Never disable another site's configuration."""
import argparse,json,pathlib,re,socket,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--domain',required=True);p.add_argument('--managed-vhost',required=True);p.add_argument('--port-file',required=True);p.add_argument('--preferred-port',type=int,default=18773);args=p.parse_args()
if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?',args.domain) or '.' not in args.domain:sys.exit('Invalid domain')
result=subprocess.run(['nginx','-T'],capture_output=True,text=True)
if result.returncode:sys.exit('Existing Nginx configuration is invalid. Fix nginx -t before deployment.\n'+result.stderr)
file='';conflicts=[];managed=pathlib.Path(args.managed_vhost).resolve()
for line in result.stdout.splitlines():
 m=re.match(r'# configuration file (.*):$',line)
 if m:file=m.group(1)
 m=re.search(r'\bserver_name\s+([^;]+);',line.split('#')[0])
 if m and args.domain in m.group(1).split() and pathlib.Path(file).resolve()!=managed:conflicts.append(file)
if conflicts:sys.exit('Duplicate exact server_name for '+args.domain+' in: '+', '.join(sorted(set(conflicts)))+'. Back up and remove only this domain from those vhosts, then rerun; other domains were not modified.')
portfile=pathlib.Path(args.port_file);old=int(portfile.read_text().strip()) if portfile.exists() else None
active=subprocess.run(['systemctl','is-active','--quiet','effortlesssmiles.service']).returncode==0
if old and active:port=old
else:
 candidates=[old] if old else list(range(args.preferred_port,args.preferred_port+11));port=None
 for value in candidates:
  if not value or not 1024<=value<=65535:continue
  s=socket.socket()
  try:s.bind(('127.0.0.1',value));port=value;break
  except OSError:pass
  finally:s.close()
 if port is None:sys.exit('No available reserved loopback port. Check ss -ltnp; current port file was preserved.')
print(json.dumps({'domain':args.domain,'port':port,'existing_service':active,'managed_vhost':args.managed_vhost,'wildcard_vhosts':'Exact-domain routing will be verified with a local sentinel request.'}))
