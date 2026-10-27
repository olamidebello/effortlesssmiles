#!/usr/bin/env python3
"""Build and verify a signed Android companion; no merchant or account secrets embedded."""
import os,subprocess,shutil,hashlib,json,re,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];src=root/'mobile/android';out=root/'public/downloads';work=src/'build';sdk=Path(os.environ.get('ANDROID_HOME','/workspace/android-build/sdk'));tools=sdk/'build-tools/35.0.0';android=sdk/'platforms/android-35/android.jar';ecj=Path(os.environ.get('ECJ_JAR','/workspace/android-build/ecj.jar'))
key=Path(os.environ.get('ES_KEYSTORE',str(src/'signing/effortless-preview.p12')));password=os.environ.get('ES_KEY_PASSWORD','android-preview-only');env=dict(os.environ,ES_SIGNING_PASSWORD=password)
def run(args):return subprocess.run([str(x) for x in args],check=True,env=env,capture_output=True,text=True).stdout
if work.exists():shutil.rmtree(work)
for p in [work/'generated',work/'classes',work/'dex',out,key.parent]:p.mkdir(parents=True,exist_ok=True)
if not key.exists():
 run(['keytool','-genkeypair','-noprompt','-keystore',key,'-storetype','PKCS12','-storepass:env','ES_SIGNING_PASSWORD','-keypass:env','ES_SIGNING_PASSWORD','-alias','effortless-preview','-keyalg','RSA','-keysize','2048','-validity','10000','-dname','CN=Effortless Smiles Development Preview,O=Effortless Smiles,C=US'])
 key.chmod(0o600)
run([tools/'aapt','package','-f','-M',src/'AndroidManifest.xml','-S',src/'res','-I',android,'-J',work/'generated','-F',work/'resources.apk'])
java=list((src/'src').rglob('*.java'))+list((work/'generated').rglob('*.java'))
run(['java','-jar',ecj,'-source','1.8','-target','1.8','-proc:none','-bootclasspath',android,'-d',work/'classes',*java])
run([tools/'d8','--lib',android,'--min-api','26','--output',work/'dex',*list((work/'classes').rglob('*.class'))])
shutil.copy(work/'resources.apk',work/'unsigned.apk')
with zipfile.ZipFile(work/'unsigned.apk','a',compression=zipfile.ZIP_DEFLATED) as z:z.write(work/'dex/classes.dex','classes.dex')
run([tools/'zipalign','-f','-p','4',work/'unsigned.apk',work/'aligned.apk'])
apk=out/'effortless-smiles-preview.apk'
run([tools/'apksigner','sign','--ks',key,'--ks-key-alias','effortless-preview','--ks-pass','env:ES_SIGNING_PASSWORD','--out',apk,work/'aligned.apk'])
verification=run([tools/'apksigner','verify','--verbose','--print-certs',apk]);cert=re.search(r'Signer #1 certificate SHA-256 digest: ([a-fA-F0-9]+)',verification).group(1)
badging=run([tools/'aapt','dump','badging',apk]);assert "package: name='com.effortlesssmiles.mobile.preview'" in badging;assert "sdkVersion:'26'" in badging
checksum=hashlib.sha256(apk.read_bytes()).hexdigest();(out/(apk.name+'.sha256')).write_text(checksum+'  '+apk.name+'\n')
info={'name':'Effortless Smiles','package':'com.effortlesssmiles.mobile.preview','version':'0.1.0','version_code':1,'channel':'development-preview','artifact_kind':'effortless-smiles-companion','sha256':checksum,'signing_certificate_sha256':cert,'size_bytes':apk.stat().st_size,'min_android':'8.0','website':'https://effortless-smiles-studio.hazy-tern-4233.chatgpt.site','apk_url':'https://effortless-smiles-studio.hazy-tern-4233.chatgpt.site/downloads/'+apk.name,'demo_payments_enabled':False,'demo_purchases_enabled':False,'limitations':'Browser-based companion; internet and platform access required. No native offline transactions, push notifications or background services. Not a Google Play release.'};(out/'release.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
