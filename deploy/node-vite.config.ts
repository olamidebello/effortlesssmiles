import {defineConfig} from 'vite';
import vinext from 'vinext';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export default defineConfig({root,plugins:[vinext()],resolve:{alias:[{find:'cloudflare:workers',replacement:path.join(root,'deploy/node-env.mjs')},{find:/^(?:\.\.\/)+app\/chatgpt-auth$/,replacement:path.join(root,'deploy/local-auth.ts')}]}});
