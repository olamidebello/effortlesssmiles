export const demoRoles:string[];
export const blockedDemoActions:Set<string>;
export function permitDemo(role:string,action:string):void;
export function createDemo(role:string,catalog:any[],settings:any):any;
export function applyDemo(state:any,action:string,payload:any):{state:any;message:string};
