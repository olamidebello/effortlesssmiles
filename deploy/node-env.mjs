import {DatabaseSync} from 'node:sqlite';
import path from 'node:path';
let singleton;
export function sqlite(){if(!singleton){const dir=process.env.ES_DATA_DIR;if(!dir||!path.isAbsolute(dir))throw new Error('ES_DATA_DIR must be an absolute persistent directory');singleton=new DatabaseSync(path.join(dir,'studio.sqlite3'));singleton.exec('PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=10000;');}return singleton;}
export class Statement{
 constructor(sql,values=[]){this.sql=sql;this.values=values;}
 bind(...values){return new Statement(this.sql,values);}
 async first(column){const row=sqlite().prepare(this.sql).get(...this.values);return row?(column?row[column]:row):null;}
 async all(){return {results:sqlite().prepare(this.sql).all(...this.values),success:true};}
 execute(){const r=sqlite().prepare(this.sql).run(...this.values);return {success:true,meta:{changes:Number(r.changes),last_row_id:Number(r.lastInsertRowid)}};}
 async run(){return this.execute();}
}
export const DB={prepare(sql){return new Statement(sql);},async batch(statements){const db=sqlite();db.exec('BEGIN IMMEDIATE');try{const results=statements.map(s=>s.execute());db.exec('COMMIT');return results;}catch(e){db.exec('ROLLBACK');throw e;}}};
export const env=new Proxy({DB},{get(target,key){if(key==='DB')return DB;if(key==='OWNER_BOOTSTRAP'||key==='ADMIN_EMAIL')return '';return process.env[key];}});
