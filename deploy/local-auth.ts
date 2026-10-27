import {headers} from 'next/headers';
import {lookupSession} from './sessions.mjs';
export async function getChatGPTUser(){const h=await headers();const member=lookupSession(h.get('cookie')||'');if(!member)return null;return {userId:member.id,email:member.email,displayName:member.name,fullName:member.name};}
