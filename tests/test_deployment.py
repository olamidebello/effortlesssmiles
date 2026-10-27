import contextlib,io,json,pathlib,runpy,subprocess,tempfile,unittest
from unittest.mock import patch,MagicMock
from jinja2 import Environment,FileSystemLoader,StrictUndefined
ROOT=pathlib.Path(__file__).resolve().parents[1]
class PreflightTests(unittest.TestCase):
 def execute(self,config,port=None,active=False,busy=False):
  with tempfile.TemporaryDirectory() as temp:
   file=pathlib.Path(temp)/'port'
   if port:file.write_text(str(port)+'\n')
   args=['preflight.py','--domain','studio.example','--managed-vhost',temp+'/managed.conf','--port-file',str(file)]
   def run(cmd,**kwargs):return subprocess.CompletedProcess(cmd,0,config,'') if cmd[0]=='nginx' else subprocess.CompletedProcess(cmd,0 if active else 3,'','')
   sock=MagicMock();sock.bind.side_effect=OSError('busy') if busy else None;output=io.StringIO()
   with patch('sys.argv',args),patch('subprocess.run',side_effect=run),patch('socket.socket',return_value=sock),contextlib.redirect_stdout(output):runpy.run_path(str(ROOT/'deploy/preflight.py'),run_name='__main__')
   return json.loads(output.getvalue()),sock
 def test_exact_duplicate_names_report_paths(self):
  with self.assertRaisesRegex(SystemExit,'/etc/nginx/sites-enabled/old.conf'):self.execute('# configuration file /etc/nginx/sites-enabled/old.conf:\nserver_name studio.example;')
 def test_wildcard_vhost_does_not_block_exact_domain(self):
  result,_=self.execute('# configuration file /etc/nginx/sites-enabled/panel.conf:\nserver_name *.example;');self.assertEqual(result['port'],18773)
 def test_running_app_reuses_persisted_port(self):
  result,sock=self.execute('',port=18778,active=True,busy=True);self.assertEqual(result['port'],18778);sock.bind.assert_not_called()
 def test_occupied_existing_port_is_not_silently_changed(self):
  with self.assertRaisesRegex(SystemExit,'No available reserved loopback port'):self.execute('',port=18778,busy=True)
 def test_nginx_template_routes_only_to_loopback(self):
  env=Environment(loader=FileSystemLoader(str(ROOT/'ansible/templates')),undefined=StrictUndefined)
  for tls in [False,True]:
   rendered=env.get_template('effortlesssmiles.nginx.j2').render(es_domain='studio.example',es_selected_port=18773,es_tls_ready=tls)
   self.assertIn('proxy_pass http://127.0.0.1:18773;',rendered);self.assertIn('oai-authenticated-user-id "";',rendered);self.assertIn('/.es-deploy-check',rendered);self.assertNotIn('root /opt/',rendered);self.assertEqual('listen 443 ssl;' in rendered,tls)
if __name__=='__main__':unittest.main()
