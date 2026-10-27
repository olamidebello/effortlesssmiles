import {demoRoles,permitDemo,createDemo} from '../../../lib/demo.mjs';
import {seedCatalog,defaults} from '../../../lib/catalog';
export const dynamic='force-dynamic';
export async function GET(req:Request){const role=new URL(req.url).searchParams.get('role')||'customer';if(!demoRoles.includes(role))return Response.json({error:'Invalid demo role'},{status:400});return Response.json(createDemo(role,seedCatalog,defaults),{headers:{'Cache-Control':'no-store'}});}
export async function POST(req:Request){if(req.headers.get('origin')!==new URL(req.url).origin)return Response.json({error:'Origin not permitted'},{status:403});try{const body=await req.json() as any;permitDemo(body.role,body.action);return Response.json({ok:true,simulated:true,message:'Authorized isolated demo operation. Apply only to sample records.'},{headers:{'Cache-Control':'no-store'}});}catch(e){return Response.json({error:(e as Error).message},{status:403});}}
