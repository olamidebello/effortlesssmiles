import {randomBytes,scryptSync,timingSafeEqual,createHash} from 'node:crypto';
import {sqlite} from './node-env.mjs';
export const cookieName='__Host-es_session';
export const tokenHash=token=>createHash('sha256').update(token).digest('hex');
export function hashPassword(password,salt=randomBytes(16).toString('hex')){if(typeof password!=='string'||password.length<14||password.length>256)throw new Error('Password must contain 14–256 characters');return salt+':'+scryptSync(password,salt,64,{N:16384,r:8,p:1,maxmem:64*1024*1024}).toString('hex');}
export function checkPassword(password,stored){try{const salt=stored.split(':')[0],computed=hashPassword(password,salt);return timingSafeEqual(Buffer.from(computed),Buffer.from(stored));}catch{return false;}}
export function cookies(value){return Object.fromEntries(value.split(';').map(x=>x.trim().split('=')).filter(x=>x.length===2));}
export function lookupSession(cookie){const token=cookies(cookie)[cookieName];if(!token||!/^[a-f0-9]{64}$/.test(token))return null;return sqlite().prepare('SELECT m.id,m.email,m.name,m.role,m.disabled FROM local_sessions s JOIN members m ON m.id=s.user_id WHERE s.token_hash=? AND s.expires>? AND m.disabled=0').get(tokenHash(token),Date.now());}
export function issueSession(userId){const token=randomBytes(32).toString('hex');const db=sqlite();db.prepare('DELETE FROM local_sessions WHERE expires<?').run(Date.now());db.prepare('INSERT INTO local_sessions VALUES (?,?,?)').run(tokenHash(token),userId,Date.now()+8*3600000);return `${cookieName}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=28800`;}
export function clearSession(cookie){const token=cookies(cookie)[cookieName];if(token)sqlite().prepare('DELETE FROM local_sessions WHERE token_hash=?').run(tokenHash(token));return `${cookieName}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;}
export function limited(bucket){const db=sqlite(),now=Date.now();db.prepare('DELETE FROM local_attempts WHERE started<?').run(now-900000);const row=db.prepare('SELECT attempts FROM local_attempts WHERE bucket=?').get(bucket);return (row?.attempts||0)>=10;}
export function attempt(bucket){sqlite().prepare('INSERT INTO local_attempts(bucket,attempts,started) VALUES (?,1,?) ON CONFLICT(bucket) DO UPDATE SET attempts=attempts+1').run(bucket,Date.now());}
