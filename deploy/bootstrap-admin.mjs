// Base64 transport avoids Ansible 2.14's implicit conversion of JSON strings
// into dictionaries (whose string form is not valid JSON). Never print input.
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
let input;
try {
 const encoded=fs.readFileSync(0,'utf8').trim();
 if(!/^[A-Za-z0-9+/]+={0,2}$/.test(encoded))throw new Error();
 input=Buffer.from(encoded,'base64').toString('utf8');
 const value=JSON.parse(input);
 if(!value || typeof value.email!=='string' || typeof value.password!=='string')throw new Error();
} catch { console.log('INVALID_CREDENTIAL_FILE');process.exit(1); }
const run=spawnSync(process.execPath,['deploy/manage.mjs','bootstrap-admin'],{input,encoding:'utf8',env:process.env});
if(run.status===0){console.log('ADMIN_READY');process.exit(0);}
const error=String(run.stderr||'');
const code=error.includes('Existing account is not an active super admin')?'ACCOUNT_PERMISSION_CONFLICT':error.includes('Valid administrator email required')?'INVALID_ADMIN_EMAIL':error.includes('Password must contain')?'INVALID_PASSWORD_LENGTH':error.includes('SQLITE_BUSY')||error.includes('database is locked')?'DATABASE_BUSY':error.includes('readonly')||error.includes('EACCES')?'DATABASE_PERMISSION_ERROR':error.includes('no such table')?'MIGRATIONS_REQUIRED':'ADMIN_SETUP_FAILED';
console.log(code);process.exit(1);
